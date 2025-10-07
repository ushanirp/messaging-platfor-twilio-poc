// Base URL for API - adjust according to your backend URL
const API_BASE_URL = 'http://localhost:5000/api/v1';

// API Functions
async function apiCall(endpoint, method = 'GET', data = null) {
    const options = {
        method: method,
        headers: {
            'Content-Type': 'application/json',
        }
    };
    
    if (data && (method === 'POST' || method === 'PUT')) {
        options.body = JSON.stringify(data);
    }
    
    try {
        const response = await fetch(`${API_BASE_URL}${endpoint}`, options);
        
        if (!response.ok) {
            throw new Error(`API error: ${response.status}`);
        }
        
        return await response.json();
    } catch (error) {
        console.error('API call failed:', error);
        showToast('Error: ' + error.message, 'error');
        throw error;
    }
}

// Data loading functions
async function loadDashboardData() {
    try {
        // Load counts for dashboard
        const [campaigns, users, templates, messages] = await Promise.all([
            apiCall('/campaigns'),
            apiCall('/users'),
            apiCall('/templates'),
            apiCall('/messages')
        ]);
        
        state.campaigns = campaigns || [];
        state.users = users || [];
        state.templates = templates || [];
        state.messages = messages || [];
        
        // Update stats
        if (elements.campaignsCount) elements.campaignsCount.textContent = state.campaigns.length;
        if (elements.usersCount) elements.usersCount.textContent = state.users.length;
        if (elements.templatesCount) elements.templatesCount.textContent = state.templates.length;
        if (elements.messagesCount) elements.messagesCount.textContent = state.messages.length;
        
        // Update recent campaigns table
        renderRecentCampaigns();
    } catch (error) {
        console.error('Failed to load dashboard data:', error);
    }
}

async function loadCampaigns() {
    try {
        const campaigns = await apiCall('/campaigns');
        state.campaigns = campaigns || [];
        renderCampaignsTable();
    } catch (error) {
        console.error('Failed to load campaigns:', error);
    }
}

async function loadTemplates() {
    try {
        const templates = await apiCall('/templates');
        state.templates = templates || [];
        renderTemplatesTable();
    } catch (error) {
        console.error('Failed to load templates:', error);
    }
}

async function loadSegments() {
    try {
        const segments = await apiCall('/segments');
        state.segments = segments || [];
        renderSegmentsTable();
    } catch (error) {
        console.error('Failed to load segments:', error);
    }
}

async function loadUsers() {
    try {
        const users = await apiCall('/users');
        state.users = users || [];
        renderUsersTable();
    } catch (error) {
        console.error('Failed to load users:', error);
    }
}

async function loadMessages(campaignId = null) {
    try {
        const endpoint = campaignId ? `/messages?campaign_id=${campaignId}` : '/messages';
        const messages = await apiCall(endpoint);
        state.messages = messages || [];
        renderMessagesTable();
        
        // Update campaign filter dropdown
        if (!campaignId) {
            updateCampaignFilter();
        }
    } catch (error) {
        console.error('Failed to load messages:', error);
    }
}

// Dropdown loading functions
async function loadTemplatesForDropdown() {
    try {
        const templates = await apiCall('/templates');
        const dropdown = document.getElementById('campaign-template');
        
        if (!dropdown) return;
        
        // Clear existing options except the first one
        while (dropdown.children.length > 1) {
            dropdown.removeChild(dropdown.lastChild);
        }
        
        templates.forEach(template => {
            const option = document.createElement('option');
            option.value = template.id;
            option.textContent = template.name || `Template ${template.id}`;
            dropdown.appendChild(option);
        });
    } catch (error) {
        console.error('Failed to load templates for dropdown:', error);
    }
}

async function loadSegmentsForDropdown() {
    try {
        const segments = await apiCall('/segments');
        const dropdown = document.getElementById('campaign-segment');
        
        if (!dropdown) return;
        
        // Clear existing options except the first one
        while (dropdown.children.length > 1) {
            dropdown.removeChild(dropdown.lastChild);
        }
        
        segments.forEach(segment => {
            const option = document.createElement('option');
            option.value = segment.id;
            option.textContent = segment.name || `Segment ${segment.id}`;
            dropdown.appendChild(option);
        });
    } catch (error) {
        console.error('Failed to load segments for dropdown:', error);
    }
}

function updateCampaignFilter() {
    const filter = elements.campaignFilter;
    
    if (!filter) return;
    
    // Clear existing options except the first one
    while (filter.children.length > 1) {
        filter.removeChild(filter.lastChild);
    }
    
    // Add campaign options
    state.campaigns.forEach(campaign => {
        const option = document.createElement('option');
        option.value = campaign.id;
        option.textContent = campaign.name || `Campaign ${campaign.id}`;
        filter.appendChild(option);
    });
}