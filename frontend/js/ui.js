// Tab switching
function switchTab(tabName) {
    // Update active tab in navigation
    if (elements.navLinks) {
        elements.navLinks.forEach(link => {
            if (link.getAttribute('data-tab') === tabName) {
                link.classList.add('active');
            } else {
                link.classList.remove('active');
            }
        });
    }

    // Update active content
    if (elements.tabContents) {
        elements.tabContents.forEach(content => {
            if (content.id === tabName) {
                content.classList.add('active');
            } else {
                content.classList.remove('active');
            }
        });
    }

    // Update page title
    const tabTitles = {
        'dashboard': 'Dashboard',
        'campaigns': 'Campaigns',
        'templates': 'Templates',
        'segments': 'Segments',
        'users': 'Users',
        'messages': 'Messages'
    };
    if (elements.pageTitle) {
        elements.pageTitle.textContent = tabTitles[tabName] || 'Dashboard';
    }

    // Load data for the tab if needed
    if (tabName === 'campaigns') {
        loadCampaigns();
    } else if (tabName === 'templates') {
        loadTemplates();
    } else if (tabName === 'segments') {
        loadSegments();
    } else if (tabName === 'users') {
        loadUsers();
    } else if (tabName === 'messages') {
        loadMessages();
    }
}

function switchUserTab(tabId) {
    // Update active tab
    document.querySelectorAll('[data-user-tab]').forEach(tab => {
        if (tab.getAttribute('data-user-tab') === tabId) {
            tab.classList.add('active');
        } else {
            tab.classList.remove('active');
        }
    });

    // Update active content
    document.querySelectorAll('#users .tab-content').forEach(content => {
        if (content.id === tabId) {
            content.classList.add('active');
        } else {
            content.classList.remove('active');
        }
    });
}

function switchMessageTab(tabId) {
    // Update active tab
    document.querySelectorAll('[data-message-tab]').forEach(tab => {
        if (tab.getAttribute('data-message-tab') === tabId) {
            tab.classList.add('active');
        } else {
            tab.classList.remove('active');
        }
    });

    // Update active content
    document.querySelectorAll('#messages .tab-content').forEach(content => {
        if (content.id === tabId) {
            content.classList.add('active');
        } else {
            content.classList.remove('active');
        }
    });
}

// Modal functions
function openModal(modalId) {
    const modal = document.getElementById(modalId);
    if (modal) {
        modal.style.display = 'flex';
        
        // Load dropdown data if needed
        if (modalId === 'create-campaign-modal') {
            loadTemplatesForDropdown();
            loadSegmentsForDropdown();
        }
    }
}

function closeModals() {
    if (elements.modals) {
        elements.modals.forEach(modal => {
            modal.style.display = 'none';
        });
    }
    
    // Reset forms
    document.querySelectorAll('form').forEach(form => {
        form.reset();
    });
}

// Utility functions
function formatDate(dateString) {
    if (!dateString) return 'N/A';
    
    const date = new Date(dateString);
    return date.toLocaleDateString() + ' ' + date.toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'});
}

function showToast(message, type = 'success') {
    if (elements.toast && elements.toastMessage) {
        elements.toast.className = `toast ${type}`;
        elements.toastMessage.textContent = message;
        elements.toast.classList.add('show');
        
        setTimeout(() => {
            elements.toast.classList.remove('show');
        }, 3000);
    }
}