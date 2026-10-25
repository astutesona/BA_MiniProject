/**
 * Business Sales Intelligence - Main JavaScript Utility
 */

document.addEventListener('DOMContentLoaded', function () {
    // Enable Bootstrap tooltips if any
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // Auto-dismiss standard alerts after 6 seconds
    setTimeout(function () {
        var alerts = document.querySelectorAll('.alert-dismissible');
        alerts.forEach(function (alert) {
            var bsAlert = bootstrap.Alert.getOrCreateInstance(alert);
            bsAlert.close();
        });
    }, 6000);
});

// Demo login autofill function
function fillCredentials(username, password) {
    var uField = document.getElementById('username');
    var pField = document.getElementById('password');
    if (uField && pField) {
        uField.value = username;
        pField.value = password;
        uField.focus();
    }
}

// Quick Date Range Filter presets
function setDateFilter(preset) {
    var startInput = document.getElementById('filter_start_date');
    var endInput = document.getElementById('filter_end_date');
    if (!startInput || !endInput) return;

    var now = new Date();
    var formatDate = function (d) {
        var month = '' + (d.getMonth() + 1);
        var day = '' + d.getDate();
        var year = d.getFullYear();
        if (month.length < 2) month = '0' + month;
        if (day.length < 2) day = '0' + day;
        return [year, month, day].join('-');
    };

    endInput.value = formatDate(now);

    if (preset === 'last30') {
        var past30 = new Date();
        past30.setDate(now.getDate() - 30);
        startInput.value = formatDate(past30);
    } else if (preset === 'thisMonth') {
        var firstDay = new Date(now.getFullYear(), now.getMonth(), 1);
        startInput.value = formatDate(firstDay);
    } else if (preset === 'ytd') {
        var startYear = new Date(now.getFullYear(), 0, 1);
        startInput.value = formatDate(startYear);
    } else if (preset === 'clear') {
        startInput.value = '';
        endInput.value = '';
    }
}
