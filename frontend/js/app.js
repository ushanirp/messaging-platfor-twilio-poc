// Global state and elements
let state = {
    campaigns: [],
    templates: [],
    segments: [],
    users: [],
    messages: []
};

let elements = {};

// Initialize the application
document.addEventListener('DOMContentLoaded', function() {
    initializeApp();
});

async function initializeApp() {
    // Wait for components to load
    await loadComponents();
    
    // Initialize DOM elements
    initializeElements();
    
    // Set up event listeners
    initEventListeners();
    
    // Load initial data
    loadDashboardData();
    switchTab('dashboard');
}

async function loadComponents() {
    const components = [
        'components/sidebar.html',
        'components/dashboard.html', 
        'components/campaigns.html',
        'components/templates.html',
        'components/segments.html',
        'components/users.html',
        'components/messages.html',
        'components/modals.html'
    ];

    for (const component of components) {
        await loadComponent(component);
    }
}

async function loadComponent(file) {
    const elements = document.querySelectorAll(`[data-include="${file}"]`);
    for (const element of elements) {
        try {
            const response = await fetch(file);
            const html = await response.text();
            element.innerHTML = html;
        } catch (error) {
            console.error(`Error loading component ${file}:`, error);
        }
    }
}

function initializeElements() {
    elements = {
        // Tabs
        tabContents: document.querySelectorAll('.tab-content'),
        navLinks: document.querySelectorAll('.nav-links a'),
        pageTitle: document.getElementById('page-title'),
        
        // Stats
        campaignsCount: document.getElementById('campaigns-count'),
        usersCount: document.getElementById('users-count'),
        templatesCount: document.getElementById('templates-count'),
        messagesCount: document.getElementById('messages-count'),
        
        // Tables
        recentCampaignsTable: document.getElementById('recent-campaigns-table')?.querySelector('tbody'),
        campaignsTable: document.getElementById('campaigns-table')?.querySelector('tbody'),
        templatesTable: document.getElementById('templates-table')?.querySelector('tbody'),
        segmentsTable: document.getElementById('segments-table')?.querySelector('tbody'),
        usersTable: document.getElementById('users-table')?.querySelector('tbody'),
        messagesTable: document.getElementById('messages-table')?.querySelector('tbody'),
        
        // Modals
        modals: document.querySelectorAll('.modal'),
        createCampaignModal: document.getElementById('create-campaign-modal'),
        createTemplateModal: document.getElementById('create-template-modal'),
        createSegmentModal: document.getElementById('create-segment-modal'),
        createUserModal: document.getElementById('create-user-modal'),
        
        // Forms
        campaignForm: document.getElementById('campaign-form'),
        templateForm: document.getElementById('template-form'),
        segmentForm: document.getElementById('segment-form'),
        userForm: document.getElementById('user-form'),
        
        // Buttons
        createCampaignBtn: document.getElementById('create-campaign-btn'),
        createCampaignBtn2: document.getElementById('create-campaign-btn-2'),
        createTemplateBtn: document.getElementById('create-template-btn'),
        createSegmentBtn: document.getElementById('create-segment-btn'),
        createUserBtn: document.getElementById('create-user-btn'),
        saveCampaignBtn: document.getElementById('save-campaign-btn'),
        saveTemplateBtn: document.getElementById('save-template-btn'),
        saveSegmentBtn: document.getElementById('save-segment-btn'),
        saveUserBtn: document.getElementById('save-user-btn'),
        uploadUsersBtn: document.getElementById('upload-users-btn'),
        sendTestBtn: document.getElementById('send-test-btn'),
        
        // Other
        campaignFilter: document.getElementById('campaign-filter'),
        scheduleType: document.getElementById('campaign-schedule-type'),
        scheduleAtContainer: document.getElementById('schedule-at-container'),
        toast: document.getElementById('toast'),
        toastMessage: document.getElementById('toast-message')
    };
}

// Event Listeners
function initEventListeners() {
    // Tab navigation
    if (elements.navLinks) {
        elements.navLinks.forEach(link => {
            link.addEventListener('click', function(e) {
                e.preventDefault();
                const tab = this.getAttribute('data-tab');
                switchTab(tab);
            });
        });
    }

    // User tabs
    document.querySelectorAll('[data-user-tab]').forEach(tab => {
        tab.addEventListener('click', function() {
            const tabId = this.getAttribute('data-user-tab');
            switchUserTab(tabId);
        });
    });

    // Message tabs
    document.querySelectorAll('[data-message-tab]').forEach(tab => {
        tab.addEventListener('click', function() {
            const tabId = this.getAttribute('data-message-tab');
            switchMessageTab(tabId);
        });
    });

    // Modal open buttons - use event delegation for dynamically loaded buttons
    document.addEventListener('click', function(e) {
        if (e.target.id === 'create-campaign-btn' || e.target.id === 'create-campaign-btn-2') {
            openModal('create-campaign-modal');
        } else if (e.target.id === 'create-template-btn') {
            openModal('create-template-modal');
        } else if (e.target.id === 'create-segment-btn') {
            openModal('create-segment-modal');
        } else if (e.target.id === 'create-user-btn') {
            openModal('create-user-modal');
        }
    });

    // Modal close buttons
    document.querySelectorAll('.close-modal').forEach(btn => {
        btn.addEventListener('click', closeModals);
    });

    // Close modal when clicking outside
    if (elements.modals) {
        elements.modals.forEach(modal => {
            modal.addEventListener('click', function(e) {
                if (e.target === this) {
                    closeModals();
                }
            });
        });
    }

    // Form submissions - use event delegation
    document.addEventListener('click', function(e) {
        if (e.target.id === 'save-campaign-btn') {
            createCampaign();
        } else if (e.target.id === 'save-template-btn') {
            createTemplate();
        } else if (e.target.id === 'save-segment-btn') {
            createSegment();
        } else if (e.target.id === 'save-user-btn') {
            createUser();
        } else if (e.target.id === 'upload-users-btn') {
            uploadUsers();
        } else if (e.target.id === 'send-test-btn') {
            sendTestMessage();
        }
    });

    // Schedule type change
    if (elements.scheduleType) {
        elements.scheduleType.addEventListener('change', function() {
            if (elements.scheduleAtContainer) {
                elements.scheduleAtContainer.style.display = 
                    this.value === 'scheduled' ? 'block' : 'none';
            }
        });
    }

    // Campaign filter change
    if (elements.campaignFilter) {
        elements.campaignFilter.addEventListener('change', function() {
            loadMessages(this.value);
        });
    }
}

// Create functions
async function createCampaign() {
    try {
        const formData = {
            name: document.getElementById('campaign-name')?.value,
            template_id: document.getElementById('campaign-template')?.value,
            segment_id: document.getElementById('campaign-segment')?.value,
            topic: document.getElementById('campaign-topic')?.value || 'general'
        };
        
        const scheduleType = document.getElementById('campaign-schedule-type')?.value;
        if (scheduleType === 'scheduled') {
            const scheduleAt = document.getElementById('campaign-schedule-at')?.value;
            if (scheduleAt) {
                formData.scheduled_at = new Date(scheduleAt).toISOString();
            }
        }
        
        await apiCall('/campaigns', 'POST', formData);
        
        showToast('Campaign created successfully');
        closeModals();
        loadCampaigns();
        loadDashboardData();
    } catch (error) {
        console.error('Failed to create campaign:', error);
    }
}

async function createTemplate() {
    try {
        const formData = {
            name: document.getElementById('template-name')?.value,
            channel: document.getElementById('template-channel')?.value,
            locale: document.getElementById('template-locale')?.value,
            body: document.getElementById('template-body')?.value
        };
        
        const placeholders = document.getElementById('template-placeholders')?.value;
        if (placeholders) {
            formData.placeholders = placeholders.split(',').map(p => p.trim());
        }
        
        await apiCall('/templates', 'POST', formData);
        
        showToast('Template created successfully');
        closeModals();
        loadTemplates();
        loadDashboardData();
    } catch (error) {
        console.error('Failed to create template:', error);
    }
}

async function createSegment() {
    try {
        const formData = {
            name: document.getElementById('segment-name')?.value
        };
        
        const definition = document.getElementById('segment-definition')?.value;
        if (definition) {
            try {
                formData.definition = JSON.parse(definition);
            } catch (e) {
                showToast('Invalid JSON in segment definition', 'error');
                return;
            }
        }
        
        await apiCall('/segments', 'POST', formData);
        
        showToast('Segment created successfully');
        closeModals();
        loadSegments();
        loadDashboardData();
    } catch (error) {
        console.error('Failed to create segment:', error);
    }
}

async function createUser() {
    try {
        const formData = {
            phone: document.getElementById('user-phone')?.value
        };
        
        const attributes = document.getElementById('user-attributes')?.value;
        if (attributes) {
            try {
                formData.attributes = JSON.parse(attributes);
            } catch (e) {
                showToast('Invalid JSON in attributes', 'error');
                return;
            }
        }
        
        const consent = document.getElementById('user-consent')?.value;
        if (consent) {
            try {
                formData.consent = JSON.parse(consent);
            } catch (e) {
                showToast('Invalid JSON in consent', 'error');
                return;
            }
        }
        
        await apiCall('/users', 'POST', formData);
        
        showToast('User created successfully');
        closeModals();
        loadUsers();
        loadDashboardData();
    } catch (error) {
        console.error('Failed to create user:', error);
    }
}

async function uploadUsers() {
    const fileInput = document.getElementById('csv-file');
    const file = fileInput?.files[0];
    
    if (!file) {
        showToast('Please select a CSV file', 'error');
        return;
    }
    
    try {
        const formData = new FormData();
        formData.append('file', file);
        
        const response = await fetch(`${API_BASE_URL}/users/bulk`, {
            method: 'POST',
            body: formData
        });
        
        if (!response.ok) {
            throw new Error(`Upload failed: ${response.status}`);
        }
        
        showToast('Users uploaded successfully');
        fileInput.value = '';
        loadUsers();
        loadDashboardData();
    } catch (error) {
        console.error('Failed to upload users:', error);
        showToast('Error uploading users: ' + error.message, 'error');
    }
}

async function sendTestMessage() {
    const phone = document.getElementById('test-phone')?.value;
    const message = document.getElementById('test-message')?.value;
    
    if (!phone || !message) {
        showToast('Please enter both phone number and message', 'error');
        return;
    }
    
    try {
        await apiCall('/messages/test/send', 'POST', {
            phone: phone,
            message: message
        });
        
        showToast('Test message sent successfully');
        document.getElementById('test-message').value = '';
    } catch (error) {
        console.error('Failed to send test message:', error);
    }
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