import React, { useEffect, useState, useRef } from 'react';
import { api } from '../services/api';
import { GraphData, GraphNode, GraphEdge } from '../types';
import {
  Share2,
  Filter,
  Search,
  Maximize2,
  RotateCcw,
  Info,
  Layers,
  FileText,
  Code,
  Eye,
  Building2,
  Scale,
} from 'lucide-react';

export const RegulatoryGraph: React.FC = () => {
  const [graphData, setGraphData] = useState<GraphData | null>(null);
  const [mermaidCode, setMermaidCode] = useState<string>('');
  const [viewMode, setViewMode] = useState<'canvas' | 'mermaid'>('canvas');
  const [selectedNode, setSelectedNode] = useState<GraphNode | null>(null);
  const [searchQuery, setSearchQuery] = useState('');
  const [filterType, setFilterType] = useState<string>('ALL');
  const [loading, setLoading] = useState(true);

  // Canvas zoom/pan state
  const [zoom, setZoom] = useState(1);
  const [pan, setPan] = useState({ x: 0, y: 0 });
  const isDragging = useRef(false);
  const dragStart = useRef({ x: 0, y: 0 });

  useEffect(() => {
    async function loadGraph() {
      try {
        setLoading(true);
        const [jsonGraph, mermaidGraph] = await Promise.all([
          api.getGraph('json'),
          api.getGraph('mermaid'),
        ]);
        setGraphData(jsonGraph);
        setMermaidCode((mermaidGraph as any).data || '');
      } catch (err) {
        console.error('Failed to load knowledge graph', err);
      } finally {
        setLoading(false);
      }
    }
    loadGraph();
  }, []);

  const handleMouseDown = (e: React.MouseEvent) => {
    isDragging.current = true;
    dragStart.current = { x: e.clientX - pan.x, y: e.clientY - pan.y };
  };

  const handleMouseMove = (e: React.MouseEvent) => {
    if (!isDragging.current) return;
    setPan({
      x: e.clientX - dragStart.current.x,
      y: e.clientY - dragStart.current.y,
    });
  };

  const handleMouseUp = () => {
    isDragging.current = false;
  };

  const handleZoom = (delta: number) => {
    setZoom((prev) => Math.max(0.4, Math.min(2.5, prev + delta)));
  };

  const resetView = () => {
    setZoom(1);
    setPan({ x: 0, y: 0 });
    setSelectedNode(null);
  };

  // Node styling based on type
  const getNodeColor = (type?: string) => {
    switch (type?.toUpperCase()) {
      case 'SCHEME':
        return { bg: '#4f46e5', border: '#818cf8', text: '#ffffff' }; // Indigo
      case 'DOCUMENT':
      case 'GUIDELINES':
        return { bg: '#0284c7', border: '#38bdf8', text: '#ffffff' }; // Sky
      case 'NOTIFICATION':
      case 'AMENDMENT':
        return { bg: '#059669', border: '#34d399', text: '#ffffff' }; // Emerald
      case 'CLAUSE':
        return { bg: '#d97706', border: '#fbbf24', text: '#ffffff' }; // Amber
      case 'BENEFICIARY_GROUP':
        return { bg: '#9333ea', border: '#c084fc', text: '#ffffff' }; // Purple
      default:
        return { bg: '#475569', border: '#94a3b8', text: '#ffffff' }; // Slate
    }
  };

  // Filter nodes
  const filteredNodes = (graphData?.nodes || []).filter((n) => {
    const matchesSearch =
      n.id.toLowerCase().includes(searchQuery.toLowerCase()) ||
      (n.label || '').toLowerCase().includes(searchQuery.toLowerCase()) ||
      (n.name || '').toLowerCase().includes(searchQuery.toLowerCase());
    const matchesType = filterType === 'ALL' || n.type?.toUpperCase() === filterType;
    return matchesSearch && matchesType;
  });

  const nodeMap = new Map((graphData?.nodes || []).map((n) => [n.id, n]));

  // Auto-arrange nodes in a force/grid pseudo-layout for SVG
  const calculateNodePosition = (node: GraphNode, index: number, total: number) => {
    // Circle clusters based on type
    const typeOffsets: Record<string, { angleBase: number; radius: number }> = {
      SCHEME: { angleBase: 0, radius: 120 },
      DOCUMENT: { angleBase: Math.PI / 3, radius: 260 },
      GUIDELINES: { angleBase: Math.PI / 3, radius: 260 },
      AMENDMENT: { angleBase: (2 * Math.PI) / 3, radius: 360 },
      CLAUSE: { angleBase: Math.PI, radius: 460 },
      BENEFICIARY_GROUP: { angleBase: (4 * Math.PI) / 3, radius: 520 },
    };

    const cfg = typeOffsets[node.type?.toUpperCase() || ''] || { angleBase: 0, radius: 300 };
    const step = (2 * Math.PI) / Math.max(1, total);
    const angle = cfg.angleBase + index * step;
    const x = 500 + Math.cos(angle) * cfg.radius;
    const y = 380 + Math.sin(angle) * (cfg.radius * 0.7);
    return { x, y };
  };

  return (
    <div className="space-y-6">
      {/* Header and Controls */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 bg-slate-900/80 p-4 rounded-xl border border-slate-800">
        <div>
          <h1 className="text-xl font-bold text-white flex items-center space-x-2">
            <Share2 className="w-5 h-5 text-indigo-400" />
            <span>Temporal Regulatory Knowledge Graph</span>
          </h1>
          <p className="text-xs text-slate-400 mt-0.5">
            Explore interconnected policies, guidelines, amendments, clauses, and supersession links.
          </p>
        </div>

        <div className="flex flex-wrap items-center gap-3">
          {/* Search Box */}
          <div className="relative">
            <Search className="w-3.5 h-3.5 text-slate-500 absolute left-2.5 top-2.5" />
            <input
              type="text"
              placeholder="Search entity in graph..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="pl-8 pr-3 py-1.5 bg-slate-950 border border-slate-700/80 rounded-lg text-xs text-slate-200 placeholder-slate-500 font-mono focus:outline-none focus:border-indigo-500"
            />
          </div>

          {/* Type Filter */}
          <select
            value={filterType}
            onChange={(e) => setFilterType(e.target.value)}
            className="px-3 py-1.5 bg-slate-950 border border-slate-700/80 rounded-lg text-xs text-slate-300 focus:outline-none focus:border-indigo-500"
          >
            <option value="ALL">All Entity Types</option>
            <option value="SCHEME">Schemes</option>
            <option value="DOCUMENT">Documents</option>
            <option value="AMENDMENT">Amendments</option>
            <option value="CLAUSE">Clauses</option>
            <option value="BENEFICIARY_GROUP">Beneficiary Groups</option>
          </select>

          {/* View Mode Toggle */}
          <div className="flex bg-slate-950 p-0.5 rounded-lg border border-slate-700/80">
            <button
              onClick={() => setViewMode('canvas')}
              className={`px-2.5 py-1 rounded text-xs font-medium flex items-center space-x-1 ${
                viewMode === 'canvas' ? 'bg-indigo-600 text-white' : 'text-slate-400 hover:text-slate-200'
              }`}
            >
              <Eye className="w-3.5 h-3.5" />
              <span>Canvas</span>
            </button>
            <button
              onClick={() => setViewMode('mermaid')}
              className={`px-2.5 py-1 rounded text-xs font-medium flex items-center space-x-1 ${
                viewMode === 'mermaid' ? 'bg-indigo-600 text-white' : 'text-slate-400 hover:text-slate-200'
              }`}
            >
              <Code className="w-3.5 h-3.5" />
              <span>Mermaid</span>
            </button>
          </div>
        </div>
      </div>

      {loading ? (
        <div className="flex items-center justify-center min-h-[50vh]">
          <div className="flex flex-col items-center space-y-3">
            <div className="w-8 h-8 border-2 border-indigo-500 border-t-transparent rounded-full animate-spin" />
            <span className="text-xs font-mono text-slate-400">Rendering Regulatory Knowledge Graph...</span>
          </div>
        </div>
      ) : viewMode === 'mermaid' ? (
        <div className="bg-slate-900 border border-slate-800 rounded-xl p-5 space-y-3">
          <div className="flex items-center justify-between pb-2 border-b border-slate-800">
            <span className="text-xs font-mono uppercase text-indigo-400 font-semibold">
              Mermaid Regulatory Flowchart Definition
            </span>
            <button
              onClick={() => navigator.clipboard.writeText(mermaidCode)}
              className="text-xs text-indigo-400 hover:text-indigo-300 font-medium"
            >
              Copy Mermaid
            </button>
          </div>
          <pre className="p-4 bg-slate-950 rounded-lg text-xs font-mono text-slate-300 overflow-x-auto max-h-[600px]">
            {mermaidCode || 'No graph relationships available.'}
          </pre>
        </div>
      ) : (
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
          {/* Interactive Graph Canvas (9 cols) */}
          <div className="lg:col-span-9 relative bg-slate-950 border border-slate-800 rounded-xl overflow-hidden min-h-[600px] shadow-inner">
            {/* Canvas Controls Overlay */}
            <div className="absolute top-4 left-4 z-10 flex items-center space-x-2 bg-slate-900/90 backdrop-blur-sm p-1.5 rounded-lg border border-slate-700/80 shadow-md">
              <button
                onClick={() => handleZoom(0.2)}
                className="px-2 py-1 text-slate-300 hover:text-white hover:bg-slate-800 rounded font-mono text-xs font-bold"
                title="Zoom In"
              >
                +
              </button>
              <span className="text-[11px] font-mono text-slate-400 px-1">{Math.round(zoom * 100)}%</span>
              <button
                onClick={() => handleZoom(-0.2)}
                className="px-2 py-1 text-slate-300 hover:text-white hover:bg-slate-800 rounded font-mono text-xs font-bold"
                title="Zoom Out"
              >
                -
              </button>
              <button
                onClick={resetView}
                className="p-1 text-slate-300 hover:text-white hover:bg-slate-800 rounded"
                title="Reset View"
              >
                <RotateCcw className="w-3.5 h-3.5" />
              </button>
            </div>

            {/* Legend Overlay */}
            <div className="absolute bottom-4 left-4 z-10 bg-slate-900/90 backdrop-blur-sm p-2 rounded-lg border border-slate-700/80 text-[10px] space-y-1 shadow-md">
              <span className="font-semibold text-slate-300 block font-mono uppercase text-[9px]">Entity Legend</span>
              <div className="flex flex-wrap gap-2">
                <span className="flex items-center space-x-1">
                  <span className="w-2.5 h-2.5 rounded-full bg-indigo-600" />
                  <span className="text-slate-400">Scheme</span>
                </span>
                <span className="flex items-center space-x-1">
                  <span className="w-2.5 h-2.5 rounded-full bg-sky-600" />
                  <span className="text-slate-400">Document</span>
                </span>
                <span className="flex items-center space-x-1">
                  <span className="w-2.5 h-2.5 rounded-full bg-emerald-600" />
                  <span className="text-slate-400">Amendment</span>
                </span>
                <span className="flex items-center space-x-1">
                  <span className="w-2.5 h-2.5 rounded-full bg-amber-600" />
                  <span className="text-slate-400">Clause</span>
                </span>
              </div>
            </div>

            {/* SVG Interactive Canvas */}
            <svg
              className="w-full h-[600px] cursor-grab active:cursor-grabbing"
              onMouseDown={handleMouseDown}
              onMouseMove={handleMouseMove}
              onMouseUp={handleMouseUp}
              onMouseLeave={handleMouseUp}
            >
              <defs>
                <marker
                  id="arrow"
                  viewBox="0 0 10 10"
                  refX="18"
                  refY="5"
                  markerWidth="6"
                  markerHeight="6"
                  orient="auto-start-reverse"
                >
                  <path d="M 0 0 L 10 5 L 0 10 z" fill="#64748b" />
                </marker>
              </defs>

              <g transform={`translate(${pan.x}, ${pan.y}) scale(${zoom})`}>
                {/* Render Edges */}
                {(graphData?.edges || []).map((edge, idx) => {
                  const sourceIndex = (graphData?.nodes || []).findIndex((n) => n.id === edge.source);
                  const targetIndex = (graphData?.nodes || []).findIndex((n) => n.id === edge.target);
                  if (sourceIndex === -1 || targetIndex === -1) return null;

                  const sNode = graphData!.nodes[sourceIndex];
                  const tNode = graphData!.nodes[targetIndex];

                  const sPos = calculateNodePosition(sNode, sourceIndex, graphData!.nodes.length);
                  const tPos = calculateNodePosition(tNode, targetIndex, graphData!.nodes.length);

                  const isHighlighted =
                    selectedNode?.id === edge.source || selectedNode?.id === edge.target;

                  return (
                    <g key={idx}>
                      <line
                        x1={sPos.x}
                        y1={sPos.y}
                        x2={tPos.x}
                        y2={tPos.y}
                        stroke={isHighlighted ? '#818cf8' : '#334155'}
                        strokeWidth={isHighlighted ? 2.5 : 1.2}
                        strokeDasharray={edge.relationship === 'AMENDS' ? '4 2' : undefined}
                        markerEnd="url(#arrow)"
                      />
                    </g>
                  );
                })}

                {/* Render Nodes */}
                {(graphData?.nodes || []).map((node, idx) => {
                  const pos = calculateNodePosition(node, idx, graphData!.nodes.length);
                  const colors = getNodeColor(node.type);
                  const isSelected = selectedNode?.id === node.id;
                  const isMatchSearch =
                    searchQuery &&
                    (node.id.toLowerCase().includes(searchQuery.toLowerCase()) ||
                      (node.label || '').toLowerCase().includes(searchQuery.toLowerCase()));

                  return (
                    <g
                      key={node.id}
                      transform={`translate(${pos.x}, ${pos.y})`}
                      onClick={(e) => {
                        e.stopPropagation();
                        setSelectedNode(node);
                      }}
                      className="cursor-pointer transition-all"
                    >
                      <circle
                        r={isSelected || isMatchSearch ? 22 : 16}
                        fill={colors.bg}
                        stroke={isSelected ? '#ffffff' : isMatchSearch ? '#f59e0b' : colors.border}
                        strokeWidth={isSelected ? 3 : isMatchSearch ? 2.5 : 1.5}
                        className="transition-transform hover:scale-110"
                      />
                      <text
                        y={28}
                        textAnchor="middle"
                        fill="#cbd5e1"
                        fontSize="9"
                        fontFamily="monospace"
                        className="select-none pointer-events-none drop-shadow"
                      >
                        {(node.label || node.name || node.id).slice(0, 16)}
                      </text>
                    </g>
                  );
                })}
              </g>
            </svg>
          </div>

          {/* Node Inspector Sidebar (3 cols) */}
          <div className="lg:col-span-3 bg-slate-900/80 border border-slate-800 rounded-xl p-4 space-y-4">
            <div className="flex items-center justify-between pb-2 border-b border-slate-800">
              <span className="text-xs font-mono uppercase tracking-wider text-slate-400 font-semibold">
                Entity Inspector
              </span>
              {selectedNode && (
                <button
                  onClick={() => setSelectedNode(null)}
                  className="text-[10px] text-slate-500 hover:text-slate-300"
                >
                  Clear
                </button>
              )}
            </div>

            {selectedNode ? (
              <div className="space-y-3">
                <div>
                  <span className="text-[10px] font-mono text-slate-500 uppercase block">Identifier</span>
                  <span className="font-mono text-xs font-bold text-indigo-300 break-all">{selectedNode.id}</span>
                </div>

                <div>
                  <span className="text-[10px] font-mono text-slate-500 uppercase block">Entity Type</span>
                  <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-slate-800 text-slate-200 border border-slate-700 inline-block mt-0.5">
                    {selectedNode.type}
                  </span>
                </div>

                {selectedNode.label && (
                  <div>
                    <span className="text-[10px] font-mono text-slate-500 uppercase block">Label / Title</span>
                    <p className="text-xs text-slate-200 leading-relaxed">{selectedNode.label}</p>
                  </div>
                )}

                {/* Connected Relationships in Graph */}
                <div className="pt-2 border-t border-slate-800/80">
                  <span className="text-[10px] font-mono text-slate-500 uppercase block mb-1">
                    Connected Relationships
                  </span>
                  <div className="space-y-1.5 max-h-48 overflow-y-auto">
                    {(graphData?.edges || [])
                      .filter((e) => e.source === selectedNode.id || e.target === selectedNode.id)
                      .map((e, i) => (
                        <div
                          key={i}
                          className="p-1.5 bg-slate-950 rounded border border-slate-800/80 text-[10px] font-mono"
                        >
                          <span className="text-indigo-400 font-semibold">{e.relationship || e.type || 'LINKS_TO'}</span>
                          <span className="text-slate-400 block truncate">
                            {e.source === selectedNode.id ? `-> ${e.target}` : `<- ${e.source}`}
                          </span>
                        </div>
                      ))}
                  </div>
                </div>
              </div>
            ) : (
              <div className="text-center py-12 text-slate-500 text-xs font-mono">
                Click any node on the regulatory canvas to inspect entity properties and relationships.
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
};
