// Render functions
function renderRecentCampaigns() {
    elements.recentCampaignsTable.innerHTML = '';
    
    const recentCampaigns = state.campaigns.slice(0, 5); // Show only 5 most recent
    
    recentCampaigns.forEach(campaign => {
        const row = document.createElement('tr');
        
        row.innerHTML = `
            <td>${campaign.name || 'Unnamed Campaign'}</td>
            <td><span class="status status-${campaign.status || 'draft'}">${campaign.status || 'Draft'}</span></td>
            <td>${campaign.template_id || 'No template'}</td>
            <td>${campaign.segment_id || 'No segment'}</td>
            <td>${formatDate(campaign.created_at)}</td>
            <td>
                <button class="btn btn-secondary" onclick="viewCampaign(${campaign.id})">View</button>
            </td>
        `;
        
        elements.recentCampaignsTable.appendChild(row);
    });
}

function renderCampaignsTable() {
    elements.campaignsTable.innerHTML = '';
    
    state.campaigns.forEach(campaign => {
        const row = document.createElement('tr');
        
        row.innerHTML = `
            <td>${campaign.name || 'Unnamed Campaign'}</td>
            <td><span class="status status-${campaign.status || 'draft'}">${campaign.status || 'Draft'}</span></td>
            <td>${campaign.template_id || 'No template'}</td>
            <td>${campaign.segment_id || 'No segment'}</td>
            <td>${campaign.scheduled_at ? formatDate(campaign.scheduled_at) : 'Immediate'}</td>
            <td>${formatDate(campaign.created_at)}</td>
            <td>
                <button class="btn btn-secondary" onclick="viewCampaign(${campaign.id})">View</button>
                ${campaign.status === 'draft' ? 
                    `<button class="btn btn-primary" onclick="launchCampaign(${campaign.id})">Launch</button>` : 
                    ''}
            </td>
        `;
        
        elements.campaignsTable.appendChild(row);
    });
}

function renderTemplatesTable() {
    elements.templatesTable.innerHTML = '';
    
    state.templates.forEach(template => {
        const row = document.createElement('tr');
        const bodyPreview = template.body ? 
            (template.body.length > 50 ? template.body.substring(0, 50) + '...' : template.body) : 
            '';
        
        row.innerHTML = `
            <td>${template.name || 'Unnamed Template'}</td>
            <td>${template.channel || 'whatsapp'}</td>
            <td>${template.locale || 'en'}</td>
            <td>${bodyPreview}</td>
            <td>${formatDate(template.created_at)}</td>
            <td>
                <button class="btn btn-secondary" onclick="previewTemplate(${template.id})">Preview</button>
            </td>
        `;
        
        elements.templatesTable.appendChild(row);
    });
}

function renderSegmentsTable() {
    elements.segmentsTable.innerHTML = '';
    
    state.segments.forEach(segment => {
        const row = document.createElement('tr');
        
        row.innerHTML = `
            <td>${segment.name || 'Unnamed Segment'}</td>
            <td>${segment.definition ? JSON.stringify(segment.definition).substring(0, 50) + '...' : ''}</td>
            <td>${formatDate(segment.created_at)}</td>
            <td>
                <button class="btn btn-secondary" onclick="viewSegmentMembers(${segment.id})">View Members</button>
            </td>
        `;
        
        elements.segmentsTable.appendChild(row);
    });
}

function renderUsersTable() {
    elements.usersTable.innerHTML = '';
    
    state.users.forEach(user => {
        const row = document.createElement('tr');
        
        row.innerHTML = `
            <td>${user.phone || 'No phone'}</td>
            <td>${user.attributes ? JSON.stringify(user.attributes) : '{}'}</td>
            <td>${user.consent ? JSON.stringify(user.consent) : '{}'}</td>
            <td>${formatDate(user.created_at)}</td>
            <td>
                <button class="btn btn-secondary" onclick="editUser(${user.id})">Edit</button>
            </td>
        `;
        
        elements.usersTable.appendChild(row);
    });
}

function renderMessagesTable() {
    elements.messagesTable.innerHTML = '';
    
    state.messages.forEach(message => {
        const row = document.createElement('tr');
        
        row.innerHTML = `
            <td>${message.campaign_id || 'No campaign'}</td>
            <td>${message.user_id || 'No user'}</td>
            <td>${message.state || 'unknown'}</td>
            <td>${message.provider_sid || 'Not sent'}</td>
            <td>${formatDate(message.created_at)}</td>
        `;
        
        elements.messagesTable.appendChild(row);
    });
}

// Dropdown loading functions
async function loadTemplatesForDropdown() {
    try {
        const templates = await apiCall('/templates');
        const dropdown = document.getElementById('campaign-template');
        
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

// Action functions (stubs for now)
function viewCampaign(id) {
    showToast(`Viewing campaign ${id} - This would open a detailed view`);
}

function launchCampaign(id) {
    showToast(`Launching campaign ${id} - This would trigger the launch API`);
    // In a real implementation, you would call:
    // apiCall(`/campaigns/${id}/launch`, 'POST');
}

function previewTemplate(id) {
    showToast(`Previewing template ${id} - This would show a preview modal`);
    // In a real implementation, you would call:
    // apiCall(`/templates/${id}/preview`, 'POST');
}

function viewSegmentMembers(id) {
    showToast(`Viewing segment ${id} members - This would show member list`);
    // In a real implementation, you would call:
    // apiCall(`/segments/${id}/members`);
}

function editUser(id) {
    showToast(`Editing user ${id} - This would open an edit form`);
}