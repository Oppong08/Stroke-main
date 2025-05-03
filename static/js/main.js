// main.js - Search functionality for the Stroke Unit System

document.addEventListener('DOMContentLoaded', function() {
    // Patient search functionality - handle both search-input class and patient-search ID
    const searchInputs = document.querySelectorAll('.search-input, #patient-search');
    
    searchInputs.forEach(searchInput => {
        if (searchInput) {
            searchInput.addEventListener('input', function() {
                const searchTerm = this.value.toLowerCase();
                const patientTable = document.querySelector('.patients-table') || document.querySelector('.table');
                
                if (patientTable) {
                    const rows = patientTable.querySelectorAll('tbody tr');
                    
                    rows.forEach(row => {
                        const name = row.querySelector('.patient-name')?.textContent.toLowerCase() || '';
                        const id = row.querySelector('.patient-id')?.textContent.toLowerCase() || '';
                        const allText = row.textContent.toLowerCase();
                        
                        // Show/hide rows based on search term
                        if (name.includes(searchTerm) || id.includes(searchTerm) || allText.includes(searchTerm)) {
                            row.style.display = '';
                        } else {
                            row.style.display = 'none';
                        }
                    });
                    
                    // Check if we have any visible rows after filtering
                    const visibleRows = patientTable.querySelectorAll('tbody tr:not([style*="display: none"])');
                    const emptyMessage = patientTable.querySelector('.empty-search-results');
                    
                    // If no results and no empty message yet, add one
                    if (visibleRows.length === 0 && !emptyMessage && searchTerm.length > 0) {
                        const tbody = patientTable.querySelector('tbody');
                        const tr = document.createElement('tr');
                        tr.className = 'empty-search-results';
                        tr.innerHTML = `
                            <td colspan="8" class="text-center py-4">
                                <div class="empty-state">
                                    <i class="fas fa-search"></i>
                                    <p>No results found for "${searchTerm}"</p>
                                </div>
                            </td>
                        `;
                        tbody.appendChild(tr);
                    } 
                    // If we have results or empty search, remove the message
                    else if ((visibleRows.length > 0 || searchTerm.length === 0) && emptyMessage) {
                        emptyMessage.remove();
                    }
                }
            });
        }
    });
}); 