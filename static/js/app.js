/**
 * Der Brauer - Common JavaScript Functions
 */

// Global utility functions
const DerBrauer = {
    currentTemperatureUnit: 'celsius',

    // Initialize temperature unit from server
    async initTemperatureUnit() {
        try {
            const response = await this.api.get('/config/temperature-unit');
            this.currentTemperatureUnit = response.temperature_unit;
            this.updateTemperatureUnitDisplay();
        } catch (error) {
            console.warn('Could not load temperature unit preference:', error);
        }
    },

    // Set temperature unit
    async setTemperatureUnit(unit) {
        try {
            const response = await this.api.put('/config/temperature-unit', { unit: unit });
            if (response.success) {
                this.currentTemperatureUnit = response.temperature_unit;
                this.updateTemperatureUnitDisplay();
                // Trigger a refresh of all temperature displays
                this.refreshTemperatureDisplays();
                this.showAlert(`Temperature unit changed to ${unit}`, 'success');
            } else {
                this.showAlert('Failed to change temperature unit: ' + response.error, 'error');
            }
        } catch (error) {
            console.error('Error setting temperature unit:', error);
            this.showAlert('Error changing temperature unit', 'error');
        }
    },

    // Update temperature unit display in navbar
    updateTemperatureUnitDisplay() {
        const unitElement = document.getElementById('current-unit');
        if (unitElement) {
            unitElement.textContent = this.currentTemperatureUnit === 'celsius' ? '°C' : '°F';
        }
    },

    // Refresh all temperature displays on the page
    refreshTemperatureDisplays() {
        // This will be called by individual pages to refresh their temperature data
        if (typeof window.refreshTemperatures === 'function') {
            window.refreshTemperatures();
        }
    },

    // Format temperature with unit
    formatTemperature: function(value, unit = null) {
        if (value === null || value === undefined) return '--';
        const displayUnit = unit || this.currentTemperatureUnit;
        const formatted = parseFloat(value).toFixed(1);
        const unitSymbol = displayUnit === 'celsius' ? '°C' : displayUnit === 'fahrenheit' ? '°F' : displayUnit;
        return `${formatted}${unitSymbol}`;
    },

    // Convert temperature between units
    convertTemperature: function(value, fromUnit, toUnit) {
        if (value === null || value === undefined) return value;
        if (fromUnit === toUnit) return value;

        if (fromUnit === 'celsius' && toUnit === 'fahrenheit') {
            return (value * 9/5) + 32;
        } else if (fromUnit === 'fahrenheit' && toUnit === 'celsius') {
            return (value - 32) * 5/9;
        } else {
            console.warn(`Unsupported temperature conversion: ${fromUnit} to ${toUnit}`);
            return value;
        }
    },

    // Format time duration
    formatDuration: function(seconds) {
        if (!seconds || seconds <= 0) return '00:00';

        const hours = Math.floor(seconds / 3600);
        const minutes = Math.floor((seconds % 3600) / 60);
        const secs = seconds % 60;

        if (hours > 0) {
            return `${hours.toString().padStart(2, '0')}:${minutes.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
        } else {
            return `${minutes.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
        }
    },

    // Show loading spinner
    showLoading: function(elementId) {
        const element = document.getElementById(elementId);
        if (element) {
            element.innerHTML = `
                <div class="d-flex justify-content-center">
                    <div class="spinner-border" role="status">
                        <span class="visually-hidden">Loading...</span>
                    </div>
                </div>
            `;
        }
    },

    // Hide loading spinner
    hideLoading: function(elementId, content = '') {
        const element = document.getElementById(elementId);
        if (element) {
            element.innerHTML = content;
        }
    },

    // Show alert message
    showAlert: function(message, type = 'info', duration = 5000) {
        const alertContainer = document.createElement('div');
        alertContainer.className = `alert alert-${type} alert-dismissible fade show position-fixed`;
        alertContainer.style.cssText = 'top: 20px; right: 20px; z-index: 1050; min-width: 300px;';
        alertContainer.innerHTML = `
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;

        document.body.appendChild(alertContainer);

        // Auto dismiss after duration
        if (duration > 0) {
            setTimeout(() => {
                if (alertContainer.parentNode) {
                    alertContainer.remove();
                }
            }, duration);
        }

        // Initialize Bootstrap alert
        const alert = new bootstrap.Alert(alertContainer);
    },

    // Confirm dialog
    confirm: function(message, title = 'Confirm') {
        return new Promise((resolve) => {
            const result = window.confirm(`${title}\n\n${message}`);
            resolve(result);
        });
    },

    // Debounce function calls
    debounce: function(func, wait) {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                clearTimeout(timeout);
                func(...args);
            };
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
        };
    },

    // API helper functions
    api: {
        baseUrl: '/api/v1',

        async get(endpoint) {
            const response = await fetch(`${this.baseUrl}${endpoint}`);
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }
            return await response.json();
        },

        async post(endpoint, data) {
            const response = await fetch(`${this.baseUrl}${endpoint}`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(data)
            });
            if (!response.ok) {
                const error = await response.json().catch(() => ({ detail: 'Unknown error' }));
                throw new Error(error.detail || `HTTP ${response.status}: ${response.statusText}`);
            }
            return await response.json();
        },

        async put(endpoint, data) {
            const response = await fetch(`${this.baseUrl}${endpoint}`, {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(data)
            });
            if (!response.ok) {
                const error = await response.json().catch(() => ({ detail: 'Unknown error' }));
                throw new Error(error.detail || `HTTP ${response.status}: ${response.statusText}`);
            }
            return await response.json();
        },

        async delete(endpoint) {
            const response = await fetch(`${this.baseUrl}${endpoint}`, {
                method: 'DELETE'
            });
            if (!response.ok) {
                const error = await response.json().catch(() => ({ detail: 'Unknown error' }));
                throw new Error(error.detail || `HTTP ${response.status}: ${response.statusText}`);
            }
            return await response.json();
        }
    },

    // Device control helpers
    devices: {
        async control(deviceId, action, value = null) {
            const data = { action };
            if (value !== null) {
                data.value = value;
            }

            return await DerBrauer.api.post(`/hardware/${deviceId}/control`, data);
        },

        async turnOn(deviceId) {
            return await this.control(deviceId, 'on');
        },

        async turnOff(deviceId) {
            return await this.control(deviceId, 'off');
        },

        async setValue(deviceId, value) {
            return await this.control(deviceId, 'set', value);
        }
    },

    // Timer helpers
    timers: {
        async create(name, durationMinutes) {
            return await DerBrauer.api.post('/timers', {
                id: `timer_${Date.now()}`,
                name: name,
                duration_minutes: durationMinutes,
                start_immediately: true
            });
        },

        async getAll() {
            return await DerBrauer.api.get('/timers');
        }
    },

    // Sensor helpers
    sensors: {
        async getAll() {
            return await DerBrauer.api.get('/sensors');
        }
    },

    // Equipment helpers
    equipment: {
        async getConfig() {
            return await DerBrauer.api.get('/equipment');
        },

        async addSensor(sensorData) {
            return await DerBrauer.api.post('/equipment/sensor', sensorData);
        },

        async addDevice(deviceData) {
            return await DerBrauer.api.post('/equipment/device', deviceData);
        }
    }
};

// Global error handler
window.addEventListener('error', function(e) {
    console.error('Global error:', e.error);
    DerBrauer.showAlert('An unexpected error occurred. Check the console for details.', 'danger');
});

// Unhandled promise rejection handler
window.addEventListener('unhandledrejection', function(e) {
    console.error('Unhandled promise rejection:', e.reason);
    DerBrauer.showAlert('An unexpected error occurred. Check the console for details.', 'danger');
});

// Global functions for navbar
function setTemperatureUnit(unit) {
    DerBrauer.setTemperatureUnit(unit);
}

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', async function() {
    console.log('Der Brauer application initialized');

    // Initialize temperature unit
    await DerBrauer.initTemperatureUnit();

    // Add loading class to body initially
    document.body.classList.add('loading');

    // Remove loading class after a short delay
    setTimeout(() => {
        document.body.classList.remove('loading');
    }, 500);
});
