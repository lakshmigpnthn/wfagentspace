import React, { useState } from 'react';
import { Terminal, Activity, Search, Settings, AlertCircle, Database, Server, Home, ChevronDown, ChevronRight, Info, Send, Clock } from 'lucide-react';

const GCPAgentSpace = () => {
  const [activeApp, setActiveApp] = useState('app1');
  const [isAppMenuOpen, setIsAppMenuOpen] = useState(true);
  const [query, setQuery] = useState('');
  const [queryResponses, setQueryResponses] = useState([]);
  const [actionHistory, setActionHistory] = useState([]);

  const apps = {
    app1: { name: 'Frontend Service', status: 'warning', type: 'Web Application' },
    app2: { name: 'Database Cluster', status: 'error', type: 'Data Service' }
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'healthy': return 'bg-green-500';
      case 'warning': return 'bg-yellow-500';
      case 'error': return 'bg-red-500';
      default: return 'bg-gray-500';
    }
  };

  const getCurrentTimestamp = () => {
    const now = new Date();
    return `${String(now.getHours()).padStart(2, '0')}:${String(now.getMinutes()).padStart(2, '0')}:${String(now.getSeconds()).padStart(2, '0')}`;
  };

  const handleAppAction = (action) => {
    const timestamp = getCurrentTimestamp();
    
    // Track action in history
    setActionHistory([
      {
        id: actionHistory.length + 1,
        action,
        app: apps[activeApp].name,
        timestamp,
        user: 'SRE Admin'
      },
      ...actionHistory
    ]);
  };
  
  const handleQuerySubmit = () => {
    if (!query.trim()) return;
    
    const timestamp = getCurrentTimestamp();
    
    // Generate a response based on the query
    const responses = {
      memory: "Current memory usage is at 78% with 3.2GB available. No memory leaks detected in the last 24 hours.",
      cpu: "CPU utilization at 45% with occasional spikes to 82% during peak traffic hours (14:00-16:00).",
      network: "Network throughput stable at 1.2Gbps. No packet loss detected on primary interfaces.",
      errors: "12 error events logged in the last hour. Most common: 'Connection timeout' (8 occurrences).",
      status: `${apps[activeApp].name} is currently in ${apps[activeApp].status} state with 4 instances running.`,
      heal: `Initiated healing process for ${apps[activeApp].name}. Memory optimization in progress.`,
      rca: `Root Cause Analysis for ${apps[activeApp].name}: Identified potential memory leak in worker threads.`
    };
    
    // Generate a relevant response or default
    let responseText = "Query processed. No specific information available for this request.";
    
    // Simple keyword matching for demo purposes
    Object.keys(responses).forEach(key => {
      if (query.toLowerCase().includes(key)) {
        responseText = responses[key];
      }
    });
    
    if (query.toLowerCase().includes("help")) {
      responseText = "Available commands: check memory, check cpu, check network, check errors, check status, heal application, run rca";
    }
    
    // Add response
    setQueryResponses([
      {
        id: queryResponses.length + 1,
        query,
        response: responseText,
        timestamp
      },
      ...queryResponses
    ]);
    
    // Track in action history
    setActionHistory([
      {
        id: actionHistory.length + 1,
        action: 'query',
        details: query,
        timestamp,
        user: 'SRE Admin'
      },
      ...actionHistory
    ]);
    
    // Clear input
    setQuery('');
  };

  return (
    <div className="flex h-screen w-full bg-gray-900 text-white overflow-hidden">
      {/* Left Sidebar - Minimal */}
      <div className="w-16 bg-gray-800 flex flex-col items-center py-4 border-r border-gray-700">
        <div className="p-2 rounded hover:bg-gray-700 mb-6">
          <Home size={24} />
        </div>
        <div className="p-2 rounded hover:bg-gray-700 mb-4">
          <Terminal size={24} />
        </div>
        <div className="mt-auto p-2 rounded hover:bg-gray-700">
          <Settings size={24} />
        </div>
      </div>

      {/* Left Panel - Applications */}
      <div className="w-64 bg-gray-800 overflow-y-auto border-r border-gray-700">
        <div className="p-4 border-b border-gray-700">
          <div className="flex items-center justify-between cursor-pointer" onClick={() => setIsAppMenuOpen(!isAppMenuOpen)}>
            <h2 className="font-semibold text-lg">Applications</h2>
            {isAppMenuOpen ? <ChevronDown size={20} /> : <ChevronRight size={20} />}
          </div>
        </div>
        
        {isAppMenuOpen && (
          <div className="p-2">
            <div 
              className={`p-3 rounded mb-2 cursor-pointer ${activeApp === 'app1' ? 'bg-gray-700' : 'hover:bg-gray-700'}`}
              onClick={() => setActiveApp('app1')}
            >
              <div className="flex items-center justify-between mb-1">
                <div className="flex items-center">
                  <Server size={16} className="mr-2" />
                  <span className="font-medium">{apps.app1.name}</span>
                </div>
                <div className={`h-3 w-3 rounded-full ${getStatusColor(apps.app1.status)}`}></div>
              </div>
              <div className="text-xs text-gray-400">{apps.app1.type}</div>
            </div>
            
            <div 
              className={`p-3 rounded cursor-pointer ${activeApp === 'app2' ? 'bg-gray-700' : 'hover:bg-gray-700'}`}
              onClick={() => setActiveApp('app2')}
            >
              <div className="flex items-center justify-between mb-1">
                <div className="flex items-center">
                  <Database size={16} className="mr-2" />
                  <span className="font-medium">{apps.app2.name}</span>
                </div>
                <div className={`h-3 w-3 rounded-full ${getStatusColor(apps.app2.status)}`}></div>
              </div>
              <div className="text-xs text-gray-400">{apps.app2.type}</div>
            </div>
          </div>
        )}

        {/* Actions Panel */}
        <div className="p-4 border-t border-gray-700 mt-4">
          <h2 className="font-semibold text-lg mb-4">Actions</h2>
          <div className="space-y-2">
            <button 
              className="w-full py-2 px-4 text-left rounded bg-blue-600 hover:bg-blue-700 transition-colors flex items-center"
              onClick={() => handleAppAction('heal')}
            >
              <Activity size={16} className="mr-2" />
              Heal Application
            </button>
            <button 
              className="w-full py-2 px-4 text-left rounded bg-gray-700 hover:bg-gray-600 transition-colors flex items-center"
              onClick={() => handleAppAction('rca')}
            >
              <Search size={16} className="mr-2" />
              Root Cause Analysis
            </button>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="flex-1 flex flex-col overflow-hidden">
        {/* Top Bar */}
        <div className="h-14 bg-gray-800 border-b border-gray-700 flex items-center px-6 justify-between">
          <div className="flex items-center">
            <h1 className="text-xl font-semibold">
              {apps[activeApp].name} 
              <span className={`ml-2 inline-block h-2 w-2 rounded-full ${getStatusColor(apps[activeApp].status)}`}></span>
            </h1>
          </div>
          <div className="flex items-center space-x-4">
            <button className="p-2 rounded hover:bg-gray-700">
              <AlertCircle size={20} />
            </button>
            <button className="p-2 rounded hover:bg-gray-700">
              <Info size={20} />
            </button>
          </div>
        </div>

        {/* Content Area */}
        <div className="flex-1 overflow-auto p-6 bg-gray-900">
          {/* SRE Query Interface */}
          <div className="bg-gray-800 rounded-lg overflow-hidden mb-6">
            <div className="bg-gray-700 py-2 px-4 font-semibold border-b border-gray-600">
              SRE Query Interface
            </div>
            <div className="p-4">
              <div className="flex">
                <input
                  type="text"
                  placeholder="Type your query here (e.g., check memory, check status, heal application)..."
                  className="flex-1 bg-gray-900 text-white p-2 rounded-l border border-gray-600 focus:outline-none focus:border-blue-500"
                  value={query}
                  onChange={(e) => setQuery(e.target.value)}
                  onKeyPress={(e) => e.key === 'Enter' && handleQuerySubmit()}
                />
                <button 
                  className="bg-blue-600 hover:bg-blue-700 px-4 rounded-r flex items-center"
                  onClick={handleQuerySubmit}
                >
                  <Send size={18} />
                </button>
              </div>
            </div>
          </div>
          
          {/* Query Response Display */}
          <div className="bg-gray-800 rounded-lg overflow-hidden mb-6">
            <div className="bg-gray-700 py-2 px-4 font-semibold border-b border-gray-600">
              Response
            </div>
            <div className="p-4">
              {queryResponses.length > 0 ? (
                <div className="bg-gray-900 rounded p-3 max-h-64 overflow-y-auto">
                  {queryResponses.map(item => (
                    <div key={item.id} className="mb-4 last:mb-0">
                      <div className="flex justify-between">
                        <div className="text-blue-400 text-sm font-mono">&gt; {item.query}</div>
                        <div className="text-gray-500 text-xs">{item.timestamp}</div>
                      </div>
                      <div className="mt-1 pl-3 border-l-2 border-gray-700 text-sm">
                        {item.response}
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="text-gray-500 text-center py-6">
                  No queries executed yet. Type a query above to begin.
                </div>
              )}
            </div>
          </div>
          
          {/* Action History */}
          <div className="bg-gray-800 rounded-lg overflow-hidden">
            <div className="bg-gray-700 py-2 px-4 font-semibold border-b border-gray-600 flex items-center">
              <Clock size={16} className="mr-2" />
              Action History
            </div>
            <div className="p-4">
              {actionHistory.length > 0 ? (
                <div className="max-h-48 overflow-y-auto">
                  {actionHistory.map(item => (
                    <div key={item.id} className="mb-2 last:mb-0 flex items-start text-sm">
                      <div className="w-24 text-gray-400">{item.timestamp}</div>
                      <div className="flex-1">
                        <span className="font-medium">{item.user}</span>
                        <span className="mx-1">-</span>
                        <span>
                          {item.action === 'query' ? (
                            <span>Executed query: <span className="text-blue-400">{item.details}</span></span>
                          ) : (
                            <span>Started <span className="text-purple-400">{item.action}</span> on {item.app}</span>
                          )}
                        </span>
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="text-gray-500 text-center py-4">No actions recorded yet</div>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default GCPAgentSpace;
