import React, { useState, useEffect } from 'react';
import ReactMarkdown from 'react-markdown'; // Import react-markdown
import { Terminal, Activity, Search, Settings, AlertCircle, Home, ChevronDown, ChevronRight, Info, Send, Clock, Robot } from 'lucide-react';
import axios from 'axios';

const GCPAgentSpace = () => {
  const [activeIncident, setActiveIncident] = useState(null); // Track the active incident
  const [isIncidentMenuOpen, setIsIncidentMenuOpen] = useState(true);
  const [allIncidents, setAllIncidents] = useState([]); // Store all incidents
  const [query, setQuery] = useState('');
  const [queryResponses, setQueryResponses] = useState([]);
  const [actionHistory, setActionHistory] = useState([]);
  const [selectedResponse, setSelectedResponse] = useState(null);
  const [changeRequests, setChangeRequests] = useState([]); // Store change requests

  useEffect(() => {
    // Fetch all incidents when the component loads
    const fetchAllIncidents = async () => {
      try {
        const response = await axios.get('http://127.0.0.1:5000/incidents');
        setAllIncidents(response.data); // Store all incidents in state
      } catch (error) {
        console.error('Error fetching incidents:', error);
      }
    };

    // Fetch all change requests when the component loads
    const fetchChangeRequests = async () => {
      try {
        const response = await axios.get('http://127.0.0.1:5000/change_requests');
        setChangeRequests(response.data); // Store change requests in state
      } catch (error) {
        console.error('Error fetching change requests:', error);
      }
    };

    fetchAllIncidents();
    fetchChangeRequests();
  }, []); // Run only once on component mount

  const handleIncidentClick = async (incidentId) => {
    setActiveIncident(incidentId); // Set the active incident

    const incident = allIncidents.find((item) => item.incident_id === incidentId);
    if (incident) {
      // Add incident details to the response box, including priority
      const incidentDetails = `Incident Details:
- Issue: ${incident.issue}
- Application Affected: ${incident.application_affected}
- Start Date: ${new Date(incident.start_date).toLocaleString()}
- Priority: ${incident.priority}`;

      setQueryResponses([
        {
          id: queryResponses.length + 1,
          query: `Incident Selected: ${incidentId}`,
          response: incidentDetails,
          timestamp: getCurrentTimestamp()
        },
        ...queryResponses
      ]);

      // Set the selected response for Heal Agent and Generate Runbook
      setSelectedResponse(incidentDetails);
    } else {
      console.error(`Incident with ID ${incidentId} not found.`);
    }
  };

  const getStatusColor = (priority) => {
    switch (priority) {
      case 'P1': return 'red';    // High priority
      case 'P2': return 'yellow'; // Medium priority
      case 'P3': return 'gray';   // Low priority
      default: return 'gray';     // Default color
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
        app: activeIncident, // Updated to reflect incidents
        timestamp,
        user: 'SRE Admin'
      },
      ...actionHistory
    ]);

    if (action === 'heal') {
      if (!selectedResponse) {
        alert("No response selected for healing.");
        return;
      }

      const issueDescription = selectedResponse; // Use the query response as the issue description
      try {
        // Send heal request to the backend
        const response = await axios.post('http://127.0.0.1:5000/generate_heal_script', { issue_description: issueDescription });
        if (response.data.status === 'success') {
          console.log('Heal script generated at:', response.data.path);
          alert(`Heal script generated successfully!\nFile: ${response.data.file}\nPath: ${response.data.path}`);
        } else {
          console.error('Heal script generation failed:', response.data.error);
          alert(`Heal script generation failed: ${response.data.error}`);
        }
      } catch (error) {
        console.error('Error generating heal script:', error.response?.data?.error || error.message);
        alert(`Error generating heal script: ${error.response?.data?.error || "An unknown error occurred."}`);
      }
    }
  };
  
  const handleGenerateRunbook = async () => {
    if (!selectedResponse) {
      alert("No response selected for runbook generation.");
      return;
    }
  
    const timestamp = getCurrentTimestamp();
  
    // Track action in history
    setActionHistory([
      {
        id: actionHistory.length + 1,
        action: 'generate_runbook',
        app: activeIncident,
        timestamp,
        user: 'SRE Admin'
      },
      ...actionHistory
    ]);
  
    try {
      // Send the selected response to the backend to generate the runbook
      const response = await axios.post('http://127.0.0.1:5000/generate_runbook', { issue_description: selectedResponse });
      if (response.data.status === 'success') {
        console.log('Runbook generated at:', response.data.path);
        alert(`Runbook generated successfully!\nFile: ${response.data.file}\nPath: ${response.data.path}`);
      } else {
        console.error('Runbook generation failed:', response.data.error);
        alert(`Runbook generation failed: ${response.data.error}`);
      }
    } catch (error) {
      console.error('Error generating runbook:', error.response?.data?.error || error.message);
      alert(`Error generating runbook: ${error.response?.data?.error || "An unknown error occurred."}`);
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
  
      // Set the selected response for runbook generation
      setSelectedResponse(responseText);
  
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
  
  const handleCRTracker = async () => {
    if (!activeIncident) {
      alert("No incident selected. Please select an incident first.");
      return;
    }

    const incident = allIncidents.find((item) => item.incident_id === activeIncident);
    if (!incident) {
      alert("Incident details not found.");
      return;
    }

    const timestamp = getCurrentTimestamp();

    // Track action in history
    setActionHistory([
      {
        id: actionHistory.length + 1,
        action: 'cr_tracker',
        app: activeIncident,
        timestamp,
        user: 'SRE Admin'
      },
      ...actionHistory
    ]);

    try {
      // Send incident details and change requests to the backend for analysis
      const response = await axios.post('http://127.0.0.1:5000/cr_tracker', {
        incident,
        change_requests: changeRequests
      });

      const impactAnalysis = response.data.impact_analysis;

      // Add impact analysis to the response box
      setQueryResponses([
        {
          id: queryResponses.length + 1,
          query: `CR Tracker Analysis for Incident: ${activeIncident}`,
          response: impactAnalysis,
          timestamp: getCurrentTimestamp()
        },
        ...queryResponses
      ]);
    } catch (error) {
      console.error('Error analyzing change requests:', error);
      alert("Error analyzing change requests. Please try again.");
    }
  };

  const priorityOrder = { P1: 1, P2: 2, P3: 3 }; // Define priority order

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

      {/* Left Panel - Incidents */}
      <div style={{ width: '256px', backgroundColor: '#444', overflowY: 'auto', borderRight: '1px solid #555' }}>
        <div style={{ padding: '16px', borderBottom: '1px solid #555' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', cursor: 'pointer' }} onClick={() => setIsIncidentMenuOpen(!isIncidentMenuOpen)}>
            <h2 style={{ fontWeight: 'bold', fontSize: '18px' }}>Incidents</h2>
            {isIncidentMenuOpen ? <ChevronDown size={20} /> : <ChevronRight size={20} />}
          </div>
        </div>
        
        {isIncidentMenuOpen && (
          <div style={{ padding: '8px', maxHeight: '400px', overflowY: 'auto' }}>
            {allIncidents
              .slice() // Create a copy of the array to avoid mutating the original
              .sort((a, b) => priorityOrder[a.priority] - priorityOrder[b.priority]) // Sort by priority
              .map((incident) => (
                <div
                  key={incident.incident_id}
                  style={{
                    padding: '12px',
                    borderRadius: '4px',
                    marginBottom: '8px',
                    cursor: 'pointer',
                    backgroundColor: activeIncident === incident.incident_id ? '#555' : 'transparent',
                  }}
                  onClick={() => handleIncidentClick(incident.incident_id)}
                >
                  <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '4px' }}>
                    <div style={{ display: 'flex', alignItems: 'center' }}>
                      <span style={{ fontWeight: '500' }}>{incident.incident_id}</span>
                    </div>
                    <div
                      style={{
                        height: '12px',
                        width: '12px',
                        borderRadius: '50%',
                        backgroundColor: getStatusColor(incident.priority),
                      }}
                    ></div>
                  </div>
                  <div style={{ fontSize: '12px', color: '#aaa' }}>{incident.issue}</div>
                </div>
              ))}
          </div>
        )}

        {/* Agents Panel */}
        <div style={{ padding: '16px', borderTop: '1px solid #555', marginTop: '16px' }}>
          <h2 style={{ fontWeight: 'bold', fontSize: '18px', marginBottom: '16px' }}>
            Agents
          </h2>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
            <button 
              style={{ width: '100%', padding: '8px 16px', textAlign: 'left', borderRadius: '4px', backgroundColor: '#007bff', color: '#fff', display: 'flex', alignItems: 'center', cursor: 'pointer' }}
              onClick={() => handleAppAction('heal')}
            >
              <Activity size={16} style={{ marginRight: '8px' }} />
              Heal Incident
            </button>
            <button 
              style={{ width: '100%', padding: '8px 16px', textAlign: 'left', borderRadius: '4px', backgroundColor: '#555', color: '#fff', display: 'flex', alignItems: 'center', cursor: 'pointer' }}
              onClick={handleCRTracker} // Updated to handle CR Tracker
            >
              <Search size={16} style={{ marginRight: '8px' }} />
              CR Tracker
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
              {activeIncident || 'Select an Incident'}
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
                    border: '1px solid #666',
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
                        {/* Render Markdown content */}
                        <ReactMarkdown>{item.response}</ReactMarkdown>
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

          {/* Generate Runbook Button */}
          <div style={{ textAlign: 'center', marginBottom: '24px' }}>
            <button 
              style={{
                backgroundColor: '#007bff',
                color: '#fff',
                padding: '10px 20px',
                borderRadius: '4px',
                cursor: 'pointer',
                fontSize: '16px',
                fontWeight: 'bold'
              }}
              onClick={handleGenerateRunbook}
            >
              Generate Runbook
            </button>
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
                            <span>Started <span style={{ color: '#FFFF00' }}>{item.action}</span> on {item.app}</span>
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
