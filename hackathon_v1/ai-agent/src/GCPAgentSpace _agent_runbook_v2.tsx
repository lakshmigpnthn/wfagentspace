import React, { useState, useEffect } from 'react';
import { Terminal, Activity, Search, Settings, AlertCircle, Database, Server, Home, ChevronDown, ChevronRight, Info, Send, Clock } from 'lucide-react';
import axios from 'axios';
import { exec } from 'child_process';

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
      case 'healthy': return 'green';
      case 'warning': return 'yellow';
      case 'error': return 'red';
      default: return 'gray';
    }
  };

  const getCurrentTimestamp = () => {
    const now = new Date();
    return `${String(now.getHours()).padStart(2, '0')}:${String(now.getMinutes()).padStart(2, '0')}:${String(now.getSeconds()).padStart(2, '0')}`;
  };

  const handleAppAction = async (action) => {
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

    if (action === 'heal') {
      const issueDescription = `Healing application: ${apps[activeApp].name}`;
      try {
        // Send heal request to the backend
        const response = await axios.post('http://127.0.0.1:5000/heal', { issue_description: issueDescription });
        if (response.data.status === 'success') {
          console.log('Heal action completed:', response.data.output);
          console.log('Runbook generated at:', response.data.path);
          alert(`Runbook generated successfully!\nFile: ${response.data.file}\nPath: ${response.data.path}`);
        } else {
          console.error('Heal action failed:', response.data.error);
        }
      } catch (error) {
        console.error('Error executing heal action:', error);
      }
    }
  };
  
  const handleQuerySubmit = async () => {
    if (!query.trim()) return;

    const timestamp = getCurrentTimestamp();

    try {
      // Send query to the backend
      const response = await axios.post('http://127.0.0.1:5000/query', { query });
      const responseText = response.data.response;

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

      // Check if a runbook was generated
      if (response.data.runbook_status === 'success') {
        console.log('Runbook generated at:', response.data.runbook_path);
        alert(`Runbook generated successfully!\nFile: ${response.data.runbook_file}\nPath: ${response.data.runbook_path}`);
      } else if (response.data.runbook_status === 'error') {
        console.error('Runbook generation failed:', response.data.runbook_error);
        alert(`Runbook generation failed: ${response.data.runbook_error}`);
      }

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
    } catch (error) {
      console.error('Error fetching query response:', error);
    }

    // Clear input
    setQuery('');
  };

  return (
    <div style={{ display: 'flex', height: '100vh', backgroundColor: '#333', color: '#fff' }}>
      {/* Sidebar */}
      <div style={{ width: '64px', backgroundColor: '#444', padding: '10px' }}>
        <div style={{ marginBottom: '20px', cursor: 'pointer' }}>
          <Home size={24} />
        </div>
        <div style={{ marginBottom: '20px', cursor: 'pointer' }}>
          <Terminal size={24} />
        </div>
        <div style={{ marginTop: 'auto', cursor: 'pointer' }}>
          <Settings size={24} />
        </div>
      </div>

      {/* Left Panel - Applications */}
      <div style={{ width: '256px', backgroundColor: '#444', overflowY: 'auto', borderRight: '1px solid #555' }}>
        <div style={{ padding: '16px', borderBottom: '1px solid #555' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', cursor: 'pointer' }} onClick={() => setIsAppMenuOpen(!isAppMenuOpen)}>
            <h2 style={{ fontWeight: 'bold', fontSize: '18px' }}>Applications</h2>
            {isAppMenuOpen ? <ChevronDown size={20} /> : <ChevronRight size={20} />}
          </div>
        </div>
        
        {isAppMenuOpen && (
          <div style={{ padding: '8px' }}>
            <div 
              style={{ padding: '12px', borderRadius: '4px', marginBottom: '8px', cursor: 'pointer', backgroundColor: activeApp === 'app1' ? '#555' : 'transparent' }}
              onClick={() => setActiveApp('app1')}
            >
              <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '4px' }}>
                <div style={{ display: 'flex', alignItems: 'center' }}>
                  <Server size={16} style={{ marginRight: '8px' }} />
                  <span style={{ fontWeight: '500' }}>{apps.app1.name}</span>
                </div>
                <div style={{ height: '12px', width: '12px', borderRadius: '50%', backgroundColor: getStatusColor(apps.app1.status) }}></div>
              </div>
              <div style={{ fontSize: '12px', color: '#aaa' }}>{apps.app1.type}</div>
            </div>
            
            <div 
              style={{ padding: '12px', borderRadius: '4px', cursor: 'pointer', backgroundColor: activeApp === 'app2' ? '#555' : 'transparent' }}
              onClick={() => setActiveApp('app2')}
            >
              <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '4px' }}>
                <div style={{ display: 'flex', alignItems: 'center' }}>
                  <Database size={16} style={{ marginRight: '8px' }} />
                  <span style={{ fontWeight: '500' }}>{apps.app2.name}</span>
                </div>
                <div style={{ height: '12px', width: '12px', borderRadius: '50%', backgroundColor: getStatusColor(apps.app2.status) }}></div>
              </div>
              <div style={{ fontSize: '12px', color: '#aaa' }}>{apps.app2.type}</div>
            </div>
          </div>
        )}

        {/* Actions Panel */}
        <div style={{ padding: '16px', borderTop: '1px solid #555', marginTop: '16px' }}>
          <h2 style={{ fontWeight: 'bold', fontSize: '18px', marginBottom: '16px' }}>Actions</h2>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
            <button 
              style={{ width: '100%', padding: '8px 16px', textAlign: 'left', borderRadius: '4px', backgroundColor: '#007bff', color: '#fff', display: 'flex', alignItems: 'center', cursor: 'pointer' }}
              onClick={() => handleAppAction('heal')}
            >
              <Activity size={16} style={{ marginRight: '8px' }} />
              Heal Application
            </button>
            <button 
              style={{ width: '100%', padding: '8px 16px', textAlign: 'left', borderRadius: '4px', backgroundColor: '#555', color: '#fff', display: 'flex', alignItems: 'center', cursor: 'pointer' }}
              onClick={() => handleAppAction('rca')}
            >
              <Search size={16} style={{ marginRight: '8px' }} />
              Root Cause Analysis
            </button>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div style={{ flex: 1, display: 'flex', flexDirection: 'column', overflow: 'hidden' }}>
        {/* Top Bar */}
        <div style={{ height: '56px', backgroundColor: '#444', borderBottom: '1px solid #555', display: 'flex', alignItems: 'center', padding: '0 24px', justifyContent: 'space-between' }}>
          <div style={{ display: 'flex', alignItems: 'center' }}>
            <h1 style={{ fontSize: '24px', fontWeight: 'bold' }}>
              {apps[activeApp].name} 
              <span style={{ marginLeft: '8px', display: 'inline-block', height: '8px', width: '8px', borderRadius: '50%', backgroundColor: getStatusColor(apps[activeApp].status) }}></span>
            </h1>
          </div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
            <button style={{ padding: '8px', borderRadius: '4px', backgroundColor: 'transparent', cursor: 'pointer' }}>
              <AlertCircle size={20} />
            </button>
            <button style={{ padding: '8px', borderRadius: '4px', backgroundColor: 'transparent', cursor: 'pointer' }}>
              <Info size={20} />
            </button>
          </div>
        </div>

        {/* Content Area */}
        <div style={{ flex: 1, overflow: 'auto', padding: '24px', backgroundColor: '#333' }}>
          {/* SRE Query Interface */}
          <div style={{ backgroundColor: '#444', borderRadius: '8px', overflow: 'hidden', marginBottom: '24px' }}>
            <div style={{ backgroundColor: '#555', padding: '8px 16px', fontWeight: 'bold', borderBottom: '1px solid #666' }}>
              SRE Query Interface
            </div>
            <div style={{ padding: '16px' }}>
              <div style={{ display: 'flex' }}>
                <input
                  type="text"
                  placeholder="Type your query here (e.g., check memory, check status, heal application)..."
                  style={{
                    flex: 1,
                    backgroundColor: '#333',
                    color: '#fff',
                    padding: '8px',
                    borderRadius: '4px 0 0 4px',
                    border: '1px solid #666',
                    outline: 'none'
                  }}
                  value={query}
                  onChange={(e) => setQuery(e.target.value)}
                  onKeyPress={(e) => e.key === 'Enter' && handleQuerySubmit()}
                />
                <button 
                  style={{
                    backgroundColor: '#007bff',
                    padding: '0 16px',
                    borderRadius: '0 4px 4px 0',
                    display: 'flex',
                    alignItems: 'center',
                    cursor: 'pointer'
                  }}
                  onClick={handleQuerySubmit}
                >
                  <Send size={18} />
                </button>
              </div>
            </div>
          </div>
          
          {/* Query Response Display */}
          <div style={{ backgroundColor: '#444', borderRadius: '8px', overflow: 'hidden', marginBottom: '24px' }}>
            <div style={{ backgroundColor: '#555', padding: '8px 16px', fontWeight: 'bold', borderBottom: '1px solid #666' }}>
              Response
            </div>
            <div style={{ padding: '16px' }}>
              {queryResponses.length > 0 ? (
                <div style={{ backgroundColor: '#333', borderRadius: '4px', padding: '12px', maxHeight: '256px', overflowY: 'auto' }}>
                  {queryResponses.map(item => (
                    <div key={item.id} style={{ marginBottom: '16px' }}>
                      <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                        <div style={{ color: '#007bff', fontSize: '14px', fontFamily: 'monospace' }}>&gt; {item.query}</div>
                        <div style={{ color: '#aaa', fontSize: '12px' }}>{item.timestamp}</div>
                      </div>
                      <div style={{ marginTop: '4px', paddingLeft: '12px', borderLeft: '2px solid #555', fontSize: '14px' }}>
                        {item.response}
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <div style={{ color: '#aaa', textAlign: 'center', padding: '24px' }}>
                  No queries executed yet. Type a query above to begin.
                </div>
              )}
            </div>
          </div>
          
          {/* Action History */}
          <div style={{ backgroundColor: '#444', borderRadius: '8px', overflow: 'hidden' }}>
            <div style={{ backgroundColor: '#555', padding: '8px 16px', fontWeight: 'bold', borderBottom: '1px solid #666', display: 'flex', alignItems: 'center' }}>
              <Clock size={16} style={{ marginRight: '8px' }} />
              Action History
            </div>
            <div style={{ padding: '16px' }}>
              {actionHistory.length > 0 ? (
                <div style={{ maxHeight: '192px', overflowY: 'auto' }}>
                  {actionHistory.map(item => (
                    <div key={item.id} style={{ marginBottom: '8px', display: 'flex', alignItems: 'flex-start', fontSize: '14px' }}>
                      <div style={{ width: '96px', color: '#aaa' }}>{item.timestamp}</div>
                      <div style={{ flex: 1 }}>
                        <span style={{ fontWeight: 'bold' }}>{item.user}</span>
                        <span style={{ margin: '0 4px' }}>-</span>
                        <span>
                          {item.action === 'query' ? (
                            <span>Executed query: <span style={{ color: '#007bff' }}>{item.details}</span></span>
                          ) : (
                            <span>Started <span style={{ color: '#800080' }}>{item.action}</span> on {item.app}</span>
                          )}
                        </span>
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <div style={{ color: '#aaa', textAlign: 'center', padding: '16px' }}>No actions recorded yet</div>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default GCPAgentSpace;

