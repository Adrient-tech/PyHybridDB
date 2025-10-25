// PyHybridDB Admin Panel JavaScript

const API_BASE = 'http://localhost:8000/api';

// Initialize authentication on page load
document.addEventListener('DOMContentLoaded', () => {
    initAuth();
});

// Navigation
document.querySelectorAll('.nav-item').forEach(item => {
    item.addEventListener('click', () => {
        const section = item.dataset.section;
        
        // Update active nav item
        document.querySelectorAll('.nav-item').forEach(i => i.classList.remove('active'));
        item.classList.add('active');
        
        // Show section
        document.querySelectorAll('.section').forEach(s => s.classList.remove('active'));
        document.getElementById(section).classList.add('active');
        
        // Load data for section
        if (section === 'dashboard') {
            loadDashboard();
        } else if (section === 'databases') {
            loadDatabasesList();
        }
    });
});

// Dashboard
async function loadDashboard() {
    try {
        const response = await authenticatedFetch(`${API_BASE}/databases`);
        const data = await response.json();
        
        const databases = data.databases || [];
        
        // Update stats
        document.getElementById('db-count').textContent = databases.length;
        
        let totalTables = 0;
        let totalCollections = 0;
        
        databases.forEach(db => {
            totalTables += db.stats.table_count || 0;
            totalCollections += db.stats.collection_count || 0;
        });
        
        document.getElementById('table-count').textContent = totalTables;
        document.getElementById('collection-count').textContent = totalCollections;
        
        // Display database list
        const dbList = document.getElementById('db-list');
        dbList.innerHTML = '<h3 style="margin-top: 2rem;">Recent Databases</h3>';
        
        databases.forEach(db => {
            const card = document.createElement('div');
            card.className = 'card';
            card.innerHTML = `
                <h4>📁 ${db.name}</h4>
                <p>Tables: ${db.stats.table_count} | Collections: ${db.stats.collection_count}</p>
                <p>Size: ${formatBytes(db.stats.file_size)}</p>
            `;
            dbList.appendChild(card);
        });
        
    } catch (error) {
        console.error('Error loading dashboard:', error);
        showAlert('error', 'Failed to load dashboard data');
    }
}

// Databases
async function loadDatabasesList() {
    try {
        const response = await authenticatedFetch(`${API_BASE}/databases`);
        const data = await response.json();
        
        const databases = data.databases || [];
        const container = document.getElementById('databases-list');
        
        if (databases.length === 0) {
            container.innerHTML = '<p style="margin-top: 2rem; color: #7f8c8d;">No databases found. Create one to get started!</p>';
            return;
        }
        
        let html = '<table style="margin-top: 2rem;"><thead><tr><th>Name</th><th>Tables</th><th>Collections</th><th>Size</th><th>Actions</th></tr></thead><tbody>';
        
        databases.forEach(db => {
            html += `
                <tr>
                    <td><strong>${db.name}</strong></td>
                    <td>${db.stats.table_count}</td>
                    <td>${db.stats.collection_count}</td>
                    <td>${formatBytes(db.stats.file_size)}</td>
                    <td>
                        <button class="btn btn-danger" onclick="deleteDatabase('${db.name}')">Delete</button>
                    </td>
                </tr>
            `;
        });
        
        html += '</tbody></table>';
        container.innerHTML = html;
        
    } catch (error) {
        console.error('Error loading databases:', error);
        showAlert('error', 'Failed to load databases');
    }
}

function showCreateDatabase() {
    document.getElementById('create-db-form').style.display = 'block';
}

function hideCreateDatabase() {
    document.getElementById('create-db-form').style.display = 'none';
    document.getElementById('db-name').value = '';
}

async function createDatabase() {
    const name = document.getElementById('db-name').value.trim();
    
    if (!name) {
        showAlert('error', 'Please enter a database name');
        return;
    }
    
    try {
        const response = await authenticatedFetch(`${API_BASE}/databases`, {
            method: 'POST',
            body: JSON.stringify({ name })
        });
        
        if (response.ok) {
            showAlert('success', `Database '${name}' created successfully`);
            hideCreateDatabase();
            loadDatabasesList();
            loadDatabaseSelects();
        } else {
            const error = await response.json();
            showAlert('error', error.detail || 'Failed to create database');
        }
    } catch (error) {
        console.error('Error creating database:', error);
        showAlert('error', 'Failed to create database');
    }
}

async function deleteDatabase(name) {
    if (!confirm(`Are you sure you want to delete database '${name}'?`)) {
        return;
    }
    
    try {
        const response = await authenticatedFetch(`${API_BASE}/databases/${name}`, {
            method: 'DELETE'
        });
        
        if (response.ok) {
            showAlert('success', `Database '${name}' deleted`);
            loadDatabasesList();
            loadDatabaseSelects();
        } else {
            showAlert('error', 'Failed to delete database');
        }
    } catch (error) {
        console.error('Error deleting database:', error);
        showAlert('error', 'Failed to delete database');
    }
}

// Tables
async function loadDatabaseSelects() {
    try {
        const response = await authenticatedFetch(`${API_BASE}/databases`);
        const data = await response.json();
        
        const databases = data.databases || [];
        const selects = [
            document.getElementById('table-db-select'),
            document.getElementById('collection-db-select'),
            document.getElementById('query-db-select'),
            document.getElementById('import-export-db-select')
        ];
        
        selects.forEach(select => {
            if (select) {
                const currentValue = select.value;
                select.innerHTML = '<option value="">-- Select Database --</option>';
                
                databases.forEach(db => {
                    const option = document.createElement('option');
                    option.value = db.name;
                    option.textContent = db.name;
                    select.appendChild(option);
                });
                
                if (currentValue) {
                    select.value = currentValue;
                }
            }
        });
    } catch (error) {
        console.error('Error loading database selects:', error);
    }
}

async function loadTables() {
    const dbName = document.getElementById('table-db-select').value;
    
    if (!dbName) {
        document.getElementById('tables-list').innerHTML = '';
        return;
    }
    
    try {
        const response = await authenticatedFetch(`${API_BASE}/databases/${dbName}/tables`);
        const data = await response.json();
        
        const tables = data.tables || [];
        const container = document.getElementById('tables-list');
        
        if (tables.length === 0) {
            container.innerHTML = '<p style="margin-top: 2rem; color: #7f8c8d;">No tables found in this database.</p>';
            return;
        }
        
        let html = '<div style="margin-top: 2rem;">';
        
        tables.forEach(table => {
            html += `
                <div class="card">
                    <h4>📋 ${table.name}</h4>
                    <p>Records: ${table.record_count}</p>
                    <p>Schema: ${JSON.stringify(table.schema)}</p>
                </div>
            `;
        });
        
        html += '</div>';
        container.innerHTML = html;
        
    } catch (error) {
        console.error('Error loading tables:', error);
        showAlert('error', 'Failed to load tables');
    }
}

function showCreateTable() {
    const dbName = document.getElementById('table-db-select').value;
    if (!dbName) {
        showAlert('error', 'Please select a database first');
        return;
    }
    document.getElementById('create-table-form').style.display = 'block';
}

function hideCreateTable() {
    document.getElementById('create-table-form').style.display = 'none';
    document.getElementById('table-name').value = '';
    document.getElementById('table-schema').value = '';
}

async function createTable() {
    const dbName = document.getElementById('table-db-select').value;
    const name = document.getElementById('table-name').value.trim();
    const schemaText = document.getElementById('table-schema').value.trim();
    
    if (!dbName || !name || !schemaText) {
        showAlert('error', 'Please fill in all fields');
        return;
    }
    
    try {
        const schema = JSON.parse(schemaText);
        
        const response = await authenticatedFetch(`${API_BASE}/databases/${dbName}/tables`, {
            method: 'POST',
            body: JSON.stringify({ name, schema })
        });
        
        if (response.ok) {
            showAlert('success', `Table '${name}' created successfully`);
            hideCreateTable();
            loadTables();
        } else {
            const error = await response.json();
            showAlert('error', error.detail || 'Failed to create table');
        }
    } catch (error) {
        console.error('Error creating table:', error);
        showAlert('error', 'Invalid schema format. Please use valid JSON.');
    }
}

// Collections
async function loadCollections() {
    const dbName = document.getElementById('collection-db-select').value;
    
    if (!dbName) {
        document.getElementById('collections-list').innerHTML = '';
        return;
    }
    
    try {
        const response = await authenticatedFetch(`${API_BASE}/databases/${dbName}/collections`);
        const data = await response.json();
        
        const collections = data.collections || [];
        const container = document.getElementById('collections-list');
        
        if (collections.length === 0) {
            container.innerHTML = '<p style="margin-top: 2rem; color: #7f8c8d;">No collections found in this database.</p>';
            return;
        }
        
        let html = '<div style="margin-top: 2rem;">';
        
        collections.forEach(collection => {
            html += `
                <div class="card">
                    <h4>📦 ${collection}</h4>
                </div>
            `;
        });
        
        html += '</div>';
        container.innerHTML = html;
        
    } catch (error) {
        console.error('Error loading collections:', error);
        showAlert('error', 'Failed to load collections');
    }
}

function showCreateCollection() {
    const dbName = document.getElementById('collection-db-select').value;
    if (!dbName) {
        showAlert('error', 'Please select a database first');
        return;
    }
    document.getElementById('create-collection-form').style.display = 'block';
}

function hideCreateCollection() {
    document.getElementById('create-collection-form').style.display = 'none';
    document.getElementById('collection-name').value = '';
}

async function createCollection() {
    const dbName = document.getElementById('collection-db-select').value;
    const name = document.getElementById('collection-name').value.trim();
    
    if (!dbName || !name) {
        showAlert('error', 'Please fill in all fields');
        return;
    }
    
    try {
        const response = await authenticatedFetch(`${API_BASE}/databases/${dbName}/collections`, {
            method: 'POST',
            body: JSON.stringify({ name })
        });
        
        if (response.ok) {
            showAlert('success', `Collection '${name}' created successfully`);
            hideCreateCollection();
            loadCollections();
        } else {
            const error = await response.json();
            showAlert('error', error.detail || 'Failed to create collection');
        }
    } catch (error) {
        console.error('Error creating collection:', error);
        showAlert('error', 'Failed to create collection');
    }
}

// Query Runner
async function executeQuery() {
    const dbName = document.getElementById('query-db-select').value;
    const query = document.getElementById('query-input').value.trim();
    
    if (!dbName) {
        showAlert('error', 'Please select a database');
        return;
    }
    
    if (!query) {
        showAlert('error', 'Please enter a query');
        return;
    }
    
    try {
        const response = await authenticatedFetch(`${API_BASE}/databases/${dbName}/query`, {
            method: 'POST',
            body: JSON.stringify({ query })
        });
        
        const data = await response.json();
        
        if (response.ok) {
            displayQueryResult(data.result);
        } else {
            showAlert('error', data.detail || 'Query execution failed');
        }
    } catch (error) {
        console.error('Error executing query:', error);
        showAlert('error', 'Failed to execute query');
    }
}

function displayQueryResult(result) {
    const container = document.getElementById('query-result');
    container.innerHTML = '<div class="query-result"><pre>' + JSON.stringify(result, null, 2) + '</pre></div>';
}

function clearQuery() {
    document.getElementById('query-input').value = '';
    document.getElementById('query-result').innerHTML = '';
}

// Utility functions
function showAlert(type, message) {
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type}`;
    alertDiv.textContent = message;
    
    const container = document.querySelector('.section.active');
    container.insertBefore(alertDiv, container.firstChild);
    
    setTimeout(() => {
        alertDiv.remove();
    }, 5000);
}

function formatBytes(bytes) {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i];
}

// Import/Export Functions
async function loadImportExportOptions() {
    const dbName = document.getElementById('import-export-db-select').value;
    
    if (!dbName) {
        return;
    }
    
    // Load database selects for import/export
    loadDatabaseSelects();
}

async function exportData() {
    const dbName = document.getElementById('import-export-db-select').value;
    const exportType = document.getElementById('export-type').value;
    const exportFormat = document.getElementById('export-format').value;
    
    if (!dbName) {
        showAlert('error', 'Please select a database');
        return;
    }
    
    try {
        let data;
        let filename;
        
        if (exportType === 'database') {
            // Export entire database
            const response = await authenticatedFetch(`${API_BASE}/databases/${dbName}`);
            data = await response.json();
            filename = `${dbName}_export.json`;
        } else if (exportType === 'table') {
            const target = document.getElementById('export-target').value;
            if (!target) {
                showAlert('error', 'Please select a table');
                return;
            }
            
            const response = await authenticatedFetch(`${API_BASE}/databases/${dbName}/tables/${target}/records`);
            data = await response.json();
            filename = `${dbName}_${target}_export.${exportFormat}`;
            
            if (exportFormat === 'csv') {
                data = convertToCSV(data.records);
            }
        } else if (exportType === 'collection') {
            const target = document.getElementById('export-target').value;
            if (!target) {
                showAlert('error', 'Please select a collection');
                return;
            }
            
            const response = await authenticatedFetch(`${API_BASE}/databases/${dbName}/collections/${target}/documents`);
            data = await response.json();
            filename = `${dbName}_${target}_export.json`;
        }
        
        // Download file
        const blob = new Blob([typeof data === 'string' ? data : JSON.stringify(data, null, 2)], {
            type: exportFormat === 'csv' ? 'text/csv' : 'application/json'
        });
        
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = filename;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        window.URL.revokeObjectURL(url);
        
        showAlert('success', `Data exported successfully to ${filename}`);
        
    } catch (error) {
        console.error('Export error:', error);
        showAlert('error', 'Failed to export data');
    }
}

async function importData() {
    const dbName = document.getElementById('import-export-db-select').value;
    const importType = document.getElementById('import-type').value;
    const targetName = document.getElementById('import-target-name').value.trim();
    const fileInput = document.getElementById('import-file');
    
    if (!dbName) {
        showAlert('error', 'Please select a database');
        return;
    }
    
    if (!targetName) {
        showAlert('error', 'Please enter a target name');
        return;
    }
    
    if (!fileInput.files || fileInput.files.length === 0) {
        showAlert('error', 'Please select a file');
        return;
    }
    
    const file = fileInput.files[0];
    const reader = new FileReader();
    
    reader.onload = async (e) => {
        try {
            const content = e.target.result;
            let data;
            
            if (file.name.endsWith('.json')) {
                data = JSON.parse(content);
            } else if (file.name.endsWith('.csv')) {
                data = parseCSV(content);
            } else {
                showAlert('error', 'Unsupported file format');
                return;
            }
            
            // Import data
            if (importType === 'table') {
                // Import to table
                if (Array.isArray(data)) {
                    for (const record of data) {
                        await authenticatedFetch(`${API_BASE}/databases/${dbName}/tables/${targetName}/records`, {
                            method: 'POST',
                            body: JSON.stringify({ data: record })
                        });
                    }
                }
            } else if (importType === 'collection') {
                // Import to collection
                if (Array.isArray(data)) {
                    for (const doc of data) {
                        await authenticatedFetch(`${API_BASE}/databases/${dbName}/collections/${targetName}/documents`, {
                            method: 'POST',
                            body: JSON.stringify({ data: doc })
                        });
                    }
                }
            }
            
            showAlert('success', `Data imported successfully to ${targetName}`);
            fileInput.value = '';
            
        } catch (error) {
            console.error('Import error:', error);
            showAlert('error', 'Failed to import data: ' + error.message);
        }
    };
    
    reader.readAsText(file);
}

function convertToCSV(data) {
    if (!data || data.length === 0) return '';
    
    const headers = Object.keys(data[0]);
    const csvRows = [];
    
    // Add header row
    csvRows.push(headers.join(','));
    
    // Add data rows
    for (const row of data) {
        const values = headers.map(header => {
            const value = row[header];
            // Escape quotes and wrap in quotes if contains comma
            const escaped = ('' + value).replace(/"/g, '""');
            return `"${escaped}"`;
        });
        csvRows.push(values.join(','));
    }
    
    return csvRows.join('\\n');
}

function parseCSV(csv) {
    const lines = csv.split('\\n');
    const headers = lines[0].split(',').map(h => h.trim().replace(/"/g, ''));
    const data = [];
    
    for (let i = 1; i < lines.length; i++) {
        if (!lines[i].trim()) continue;
        
        const values = lines[i].split(',').map(v => v.trim().replace(/"/g, ''));
        const obj = {};
        
        headers.forEach((header, index) => {
            obj[header] = values[index];
        });
        
        data.push(obj);
    }
    
    return data;
}

// Update export type change handler
document.addEventListener('DOMContentLoaded', () => {
    const exportTypeSelect = document.getElementById('export-type');
    if (exportTypeSelect) {
        exportTypeSelect.addEventListener('change', async () => {
            const exportType = exportTypeSelect.value;
            const targetGroup = document.getElementById('export-target-group');
            const targetSelect = document.getElementById('export-target');
            const dbName = document.getElementById('import-export-db-select').value;
            
            if (exportType === 'database') {
                targetGroup.style.display = 'none';
            } else {
                targetGroup.style.display = 'block';
                
                if (!dbName) {
                    return;
                }
                
                // Load tables or collections
                targetSelect.innerHTML = '<option value="">-- Select --</option>';
                
                if (exportType === 'table') {
                    const response = await authenticatedFetch(`${API_BASE}/databases/${dbName}/tables`);
                    const data = await response.json();
                    data.tables.forEach(table => {
                        const option = document.createElement('option');
                        option.value = table.name;
                        option.textContent = table.name;
                        targetSelect.appendChild(option);
                    });
                } else if (exportType === 'collection') {
                    const response = await authenticatedFetch(`${API_BASE}/databases/${dbName}/collections`);
                    const data = await response.json();
                    data.collections.forEach(coll => {
                        const option = document.createElement('option');
                        option.value = coll;
                        option.textContent = coll;
                        targetSelect.appendChild(option);
                    });
                }
            }
        });
    }
});
