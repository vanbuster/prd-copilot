#!/usr/bin/env node
'use strict';

const fs = require('fs');
const path = require('path');

const inputPath = process.argv[2];
const outputPath = process.argv[3];

if (!inputPath || !outputPath) {
  console.error('Usage: node ua-arch-analyze.js <input.json> <output.json>');
  process.exit(1);
}

let data;
try {
  data = JSON.parse(fs.readFileSync(inputPath, 'utf8'));
} catch (e) {
  console.error('Failed to parse input:', e.message);
  process.exit(1);
}

const { fileNodes, importEdges, allEdges } = data;

// ── A. Directory Grouping ──
function computeCommonPrefix(paths) {
  const filtered = paths.filter(p => p.includes('/'));
  if (filtered.length === 0) return '';
  const parts = filtered.map(p => p.split('/'));
  const minLen = Math.min(...parts.map(p => p.length));
  let prefixParts = 0;
  for (let i = 0; i < minLen - 1; i++) {
    const first = parts[0][i];
    if (parts.every(p => p[i] === first)) {
      prefixParts++;
    } else {
      break;
    }
  }
  return prefixParts > 0 ? parts[0].slice(0, prefixParts).join('/') + '/' : '';
}

const allPaths = fileNodes.map(n => n.filePath);
const commonPrefix = computeCommonPrefix(allPaths);

const directoryGroups = {};
const fileNodeMap = {};
fileNodes.forEach(n => {
  fileNodeMap[n.id] = n;
  let rel = n.filePath;
  if (commonPrefix && rel.startsWith(commonPrefix)) {
    rel = rel.slice(commonPrefix.length);
  }
  const seg = rel.split('/');
  let group;
  if (seg.length > 1) {
    group = seg[0];
  } else {
    // Root-level: group by extension pattern
    const name = seg[0];
    if (name.match(/\.test\.|\.spec\.|_test\.|Test\./)) group = 'test';
    else if (name.match(/\.config\.|config\./)) group = 'config';
    else if (name === 'app.py' || name === 'main.py' || name === 'main.go' || name === 'main.rs') group = 'root-entry';
    else group = 'root';
  }
  if (!directoryGroups[group]) directoryGroups[group] = [];
  directoryGroups[group].push(n.id);
});

// ── B. Node Type Grouping ──
const nodeTypeGroups = {};
fileNodes.forEach(n => {
  if (!nodeTypeGroups[n.type]) nodeTypeGroups[n.type] = [];
  nodeTypeGroups[n.type].push(n.id);
});

// ── C. Import Adjacency / Fan-out Fan-in ──
const fileFanOut = {};
const fileFanIn = {};
const adjList = {};

importEdges.forEach(e => {
  if (!adjList[e.source]) adjList[e.source] = [];
  adjList[e.source].push(e.target);
  fileFanOut[e.source] = (fileFanOut[e.source] || 0) + 1;
  fileFanIn[e.target] = (fileFanIn[e.target] || 0) + 1;
});

// Per-directory-group import relationships
const groupImportsFrom = {};
const groupImportsTo = {};
importEdges.forEach(e => {
  const srcGroup = Object.entries(directoryGroups).find(([, ids]) => ids.includes(e.source))?.[0];
  const tgtGroup = Object.entries(directoryGroups).find(([, ids]) => ids.includes(e.target))?.[0];
  if (srcGroup && tgtGroup) {
    if (!groupImportsFrom[srcGroup]) groupImportsFrom[srcGroup] = new Set();
    groupImportsFrom[srcGroup].add(tgtGroup);
    if (!groupImportsTo[tgtGroup]) groupImportsTo[tgtGroup] = new Set();
    groupImportsTo[tgtGroup].add(srcGroup);
  }
});
const groupImportsFromStr = {};
Object.entries(groupImportsFrom).forEach(([k, v]) => groupImportsFromStr[k] = [...v]);
const groupImportsToStr = {};
Object.entries(groupImportsTo).forEach(([k, v]) => groupImportsToStr[k] = [...v]);

// ── D. Cross-Category Dependency Analysis ──
const crossCategoryMap = {};
allEdges.forEach(e => {
  const srcNode = fileNodeMap[e.source];
  const tgtNode = fileNodeMap[e.target];
  if (!srcNode || !tgtNode) return;
  const srcType = srcNode.type;
  const tgtType = tgtNode.type;
  const key = `${srcType}->${tgtType}|${e.type}`;
  if (!crossCategoryMap[key]) crossCategoryMap[key] = { fromType: srcType, toType: tgtType, edgeType: e.type, count: 0 };
  crossCategoryMap[key].count++;
});
const crossCategoryEdges = Object.values(crossCategoryMap);

// ── E. Inter-Group Import Frequency ──
const interGroupMap = {};
importEdges.forEach(e => {
  const srcGroup = Object.entries(directoryGroups).find(([, ids]) => ids.includes(e.source))?.[0];
  const tgtGroup = Object.entries(directoryGroups).find(([, ids]) => ids.includes(e.target))?.[0];
  if (srcGroup && tgtGroup) {
    const key = `${srcGroup}->${tgtGroup}`;
    if (!interGroupMap[key]) interGroupMap[key] = { from: srcGroup, to: tgtGroup, count: 0 };
    interGroupMap[key].count++;
  }
});
const interGroupImports = Object.values(interGroupMap);

// ── F. Intra-Group Import Density ──
const intraGroupDensity = {};
Object.entries(directoryGroups).forEach(([group, ids]) => {
  let internalEdges = 0;
  let totalEdges = 0;
  importEdges.forEach(e => {
    if (ids.includes(e.source) || ids.includes(e.target)) {
      totalEdges++;
      if (ids.includes(e.source) && ids.includes(e.target)) {
        internalEdges++;
      }
    }
  });
  intraGroupDensity[group] = {
    internalEdges,
    totalEdges,
    density: totalEdges > 0 ? internalEdges / totalEdges : 0
  };
});

// ── G. Directory Pattern Matching ──
const patternMap = {
  'routes': 'api', 'api': 'api', 'controllers': 'api', 'endpoints': 'api', 'handlers': 'api',
  'services': 'service', 'core': 'service', 'lib': 'service', 'domain': 'service', 'logic': 'service',
  'models': 'data', 'db': 'data', 'data': 'data', 'persistence': 'data', 'repository': 'data', 'entities': 'data',
  'components': 'ui', 'views': 'ui', 'pages': 'ui', 'ui': 'ui', 'layouts': 'ui', 'screens': 'ui',
  'middleware': 'middleware', 'plugins': 'middleware', 'interceptors': 'middleware', 'guards': 'middleware',
  'utils': 'utility', 'helpers': 'utility', 'common': 'utility', 'shared': 'utility', 'tools': 'utility',
  'config': 'config', 'constants': 'config', 'env': 'config', 'settings': 'config',
  '__tests__': 'test', 'test': 'test', 'tests': 'test', 'spec': 'test', 'specs': 'test',
  'types': 'types', 'interfaces': 'types', 'schemas': 'types', 'contracts': 'types', 'dtos': 'types',
  'hooks': 'hooks',
  'store': 'state', 'state': 'state', 'reducers': 'state', 'actions': 'state', 'slices': 'state',
  'assets': 'assets', 'static': 'assets', 'public': 'assets',
  'migrations': 'data',
  'management': 'config', 'commands': 'config',
  'templatetags': 'utility',
  'signals': 'service',
  'serializers': 'api',
  'cmd': 'entry',
  'internal': 'service',
  'pkg': 'utility',
  'prompts': 'service',
  'templates': 'types',
  'scripts': 'utility',
  'docs': 'documentation',
  'references': 'documentation',
  'research': 'documentation',
  'bin': 'entry',
};

const patternMatches = {};
Object.keys(directoryGroups).forEach(group => {
  // Check directory pattern
  if (patternMap[group]) {
    patternMatches[group] = patternMap[group];
  } else {
    // Check file-level patterns
    const ids = directoryGroups[group];
    const types = new Set();
    ids.forEach(id => {
      const node = fileNodeMap[id];
      if (!node) return;
      const name = node.name;
      if (name.match(/\.test\.|\.spec\.|_test\.|Test\./)) types.add('test');
      else if (name.match(/\.d\.ts$/)) types.add('types');
      else if (name === 'index.ts' || name === 'index.js' || name === '__init__.py') types.add('entry');
      else if (name === 'Dockerfile' || name.match(/docker-compose/)) types.add('infrastructure');
      else if (name.match(/\.md$|\.rst$/)) types.add('documentation');
      else if (name.match(/\.sql$/)) types.add('data');
      else if (name.match(/\.css$|\.scss$/)) types.add('ui');
      else if (name === 'manage.py' || name === 'wsgi.py' || name === 'asgi.py') types.add('config');
      else if (name === 'app.py') types.add('entry');
    });
    if (types.size === 1) {
      patternMatches[group] = [...types][0];
    } else {
      patternMatches[group] = 'uncategorized';
    }
  }
});

// ── H. Deployment Topology Detection ──
const infraFileNames = fileNodes.filter(n =>
  n.name === 'Dockerfile' ||
  n.name.match(/docker-compose/) ||
  n.name === 'Jenkinsfile' ||
  n.name.match(/\.tf$/) ||
  n.name.match(/\.tfvars$/) ||
  n.filePath.includes('.github/workflows') ||
  n.filePath.includes('.gitlab-ci')
).map(n => n.filePath);

const deploymentTopology = {
  hasDockerfile: fileNodes.some(n => n.name === 'Dockerfile'),
  hasCompose: fileNodes.some(n => n.name.match(/docker-compose/)),
  hasK8s: fileNodes.some(n => n.filePath.includes('k8s') || n.filePath.includes('kubernetes') || n.filePath.includes('helm')),
  hasTerraform: fileNodes.some(n => n.name.match(/\.tf$/)),
  hasCI: fileNodes.some(n => n.filePath.includes('.github/workflows') || n.name === '.gitlab-ci.yml' || n.name === 'Jenkinsfile'),
  infraFiles: infraFileNames
};

// ── I. Data Pipeline Detection ──
const schemaFiles = fileNodes.filter(n => n.name.match(/\.sql$/) || n.name.match(/\.graphql$/) || n.name.match(/\.prisma$/)).map(n => n.filePath);
const migrationFiles = fileNodes.filter(n => n.filePath.includes('migrations')).map(n => n.filePath);
const dataModelFiles = fileNodes.filter(n => n.filePath.includes('model') || n.filePath.includes('entity')).map(n => n.filePath);
const apiHandlerFiles = fileNodes.filter(n => n.filePath.includes('route') || n.filePath.includes('controller') || n.filePath.includes('handler') || n.filePath.includes('api')).map(n => n.filePath);

const dataPipeline = { schemaFiles, migrationFiles, dataModelFiles, apiHandlerFiles };

// ── J. Documentation Coverage ──
const docFileNames = new Set(fileNodes.filter(n => n.type === 'document' || n.name.match(/\.md$|\.rst$/)).map(n => n.filePath));
const groupsWithDocsSet = new Set();
Object.entries(directoryGroups).forEach(([group, ids]) => {
  ids.forEach(id => {
    const node = fileNodeMap[id];
    if (node && (node.type === 'document' || node.name.match(/\.md$|\.rst$/))) {
      groupsWithDocsSet.add(group);
    }
  });
});
const totalGroups = Object.keys(directoryGroups).length;
const groupsWithDocs = groupsWithDocsSet.size;

const docCoverage = {
  groupsWithDocs,
  totalGroups,
  coverageRatio: totalGroups > 0 ? groupsWithDocs / totalGroups : 0,
  undocumentedGroups: Object.keys(directoryGroups).filter(g => !groupsWithDocsSet.has(g))
};

// ── K. Dependency Direction ──
const depCountMap = {};
interGroupImports.forEach(e => {
  const fwd = `${e.from}->${e.to}`;
  depCountMap[fwd] = (depCountMap[fwd] || 0) + e.count;
});

const dependencyDirection = [];
const seen = new Set();
interGroupImports.forEach(e => {
  const fwd = `${e.from}->${e.to}`;
  const rev = `${e.to}->${e.from}`;
  if (seen.has(fwd) || seen.has(rev)) return;
  seen.add(fwd);
  seen.add(rev);
  const fwdCount = depCountMap[fwd] || 0;
  const revCount = depCountMap[rev] || 0;
  if (fwdCount >= revCount) {
    dependencyDirection.push({ dependent: e.from, dependsOn: e.to, fwdCount, revCount });
  } else {
    dependencyDirection.push({ dependent: e.to, dependsOn: e.from, fwdCount: revCount, revCount: fwdCount });
  }
});

// ── File Stats ──
const filesPerGroup = {};
Object.entries(directoryGroups).forEach(([g, ids]) => filesPerGroup[g] = ids.length);
const nodeTypeCounts = {};
Object.entries(nodeTypeGroups).forEach(([t, ids]) => nodeTypeCounts[t] = ids.length);

const fileStats = {
  totalFileNodes: fileNodes.length,
  filesPerGroup,
  nodeTypeCounts
};

// ── Output ──
const results = {
  scriptCompleted: true,
  directoryGroups,
  nodeTypeGroups,
  crossCategoryEdges,
  interGroupImports,
  intraGroupDensity,
  patternMatches,
  deploymentTopology,
  dataPipeline,
  docCoverage,
  dependencyDirection,
  fileStats,
  fileFanIn,
  fileFanOut
};

fs.writeFileSync(outputPath, JSON.stringify(results, null, 2));
console.log('Analysis complete. Output written to:', outputPath);
process.exit(0);
