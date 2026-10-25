/**
 * Business Sales Intelligence & Revenue Analytics System
 * Chart.js Visualizations Controller
 */

// Enterprise Theme Colors (Muted, sophisticated, non-generic)
const CHART_COLORS = {
    primary: '#1f3a52',         // Deep slate teal
    primaryLight: 'rgba(31, 58, 82, 0.12)',
    amber: '#c67d0a',           // Bronze amber
    amberLight: 'rgba(198, 125, 10, 0.15)',
    emerald: '#0d8253',         // Deep emerald
    emeraldLight: 'rgba(13, 130, 83, 0.15)',
    cogs: '#64748b',            // Slate steel
    cogsLight: 'rgba(100, 116, 139, 0.15)',
    doughnut: ['#0d8253', '#c67d0a', '#1f3a52', '#b91c1c', '#6d28d9'],
    gridLines: '#e2e8f0',
    fontColor: '#475569'
};

const currencyFormatter = (value) => {
    return '$' + Number(value).toLocaleString('en-US', { minimumFractionDigits: 0, maximumFractionDigits: 0 });
};

// Global chart registry to destroy prior instances before redrawing
const activeCharts = {};

function initDashboardCharts(apiEndpoint, filterParams = '') {
    const url = apiEndpoint + (filterParams ? '?' + filterParams : '');

    fetch(url)
        .then(response => {
            if (!response.ok) throw new Error('Network error loading chart data');
            return response.json();
        })
        .then(data => {
            renderMonthlyTrend(data.monthly_trend);
            renderCategoryRevenue(data.category_revenue);
            renderTopProducts(data.top_products);
            renderProfitability(data.profitability);
            renderOrderStatus(data.order_status);
            renderTargetVsActual(data.target_vs_actual);
            renderCustomerContribution(data.customer_contribution);
            renderRevenueGrowth(data.growth_series);
        })
        .catch(err => {
            console.error('Error rendering dashboard charts:', err);
        });
}

function destroyIfExists(chartId) {
    if (activeCharts[chartId]) {
        activeCharts[chartId].destroy();
        delete activeCharts[chartId];
    }
}

// Chart 1: Monthly Revenue Trend
function renderMonthlyTrend(data) {
    const ctx = document.getElementById('chartMonthlyTrend');
    if (!ctx) return;
    destroyIfExists('monthlyTrend');

    activeCharts['monthlyTrend'] = new Chart(ctx, {
        type: 'line',
        data: {
            labels: data.labels,
            datasets: [
                {
                    label: 'Net Sales Revenue',
                    data: data.revenue,
                    borderColor: CHART_COLORS.primary,
                    backgroundColor: CHART_COLORS.primaryLight,
                    borderWidth: 2.5,
                    fill: true,
                    tension: 0.3,
                    pointRadius: 3,
                    pointHoverRadius: 6
                },
                {
                    label: 'Gross Profit',
                    data: data.profit,
                    borderColor: CHART_COLORS.emerald,
                    backgroundColor: 'transparent',
                    borderWidth: 2,
                    borderDash: [4, 4],
                    tension: 0.3,
                    pointRadius: 2
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                tooltip: {
                    callbacks: {
                        label: function (context) {
                            return context.dataset.label + ': ' + currencyFormatter(context.raw);
                        }
                    }
                },
                legend: { position: 'top', labels: { boxWidth: 12, font: { size: 11 } } }
            },
            scales: {
                y: {
                    grid: { color: CHART_COLORS.gridLines },
                    ticks: { callback: currencyFormatter, font: { size: 10 } }
                },
                x: {
                    grid: { display: false },
                    ticks: { font: { size: 10 } }
                }
            }
        }
    });
}

// Chart 2: Revenue by Product Category
function renderCategoryRevenue(data) {
    const ctx = document.getElementById('chartCategoryRevenue');
    if (!ctx) return;
    destroyIfExists('categoryRevenue');

    activeCharts['categoryRevenue'] = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: data.labels,
            datasets: [
                {
                    label: 'Recognized Revenue',
                    data: data.revenue,
                    backgroundColor: CHART_COLORS.primary,
                    borderRadius: 4
                },
                {
                    label: 'Gross Profit',
                    data: data.profit,
                    backgroundColor: CHART_COLORS.amber,
                    borderRadius: 4
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                tooltip: {
                    callbacks: {
                        label: (ctx) => ctx.dataset.label + ': ' + currencyFormatter(ctx.raw)
                    }
                },
                legend: { position: 'top', labels: { boxWidth: 12, font: { size: 11 } } }
            },
            scales: {
                y: {
                    grid: { color: CHART_COLORS.gridLines },
                    ticks: { callback: currencyFormatter, font: { size: 10 } }
                },
                x: {
                    grid: { display: false },
                    ticks: { font: { size: 10 } }
                }
            }
        }
    });
}

// Chart 3: Top 10 Products by Revenue
function renderTopProducts(data) {
    const ctx = document.getElementById('chartTopProducts');
    if (!ctx) return;
    destroyIfExists('topProducts');

    activeCharts['topProducts'] = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: data.labels,
            datasets: [{
                label: 'Revenue',
                data: data.revenue,
                backgroundColor: CHART_COLORS.emerald,
                borderRadius: 4
            }]
        },
        options: {
            indexAxis: 'y',
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                tooltip: {
                    callbacks: {
                        label: (ctx) => 'Revenue: ' + currencyFormatter(ctx.raw)
                    }
                },
                legend: { display: false }
            },
            scales: {
                x: {
                    grid: { color: CHART_COLORS.gridLines },
                    ticks: { callback: currencyFormatter, font: { size: 10 } }
                },
                y: {
                    grid: { display: false },
                    ticks: { font: { size: 10 } }
                }
            }
        }
    });
}

// Chart 4: Product Profitability (Revenue, COGS, Gross Profit)
function renderProfitability(data) {
    const ctx = document.getElementById('chartProfitability');
    if (!ctx) return;
    destroyIfExists('profitability');

    activeCharts['profitability'] = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: data.labels,
            datasets: [
                {
                    label: 'Gross Revenue',
                    data: data.revenue,
                    backgroundColor: CHART_COLORS.primary,
                    borderRadius: 4
                },
                {
                    label: 'Cost of Goods (COGS)',
                    data: data.cogs,
                    backgroundColor: CHART_COLORS.cogs,
                    borderRadius: 4
                },
                {
                    label: 'Gross Profit',
                    data: data.profit,
                    backgroundColor: CHART_COLORS.emerald,
                    borderRadius: 4
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                tooltip: {
                    callbacks: {
                        label: (ctx) => ctx.dataset.label + ': ' + currencyFormatter(ctx.raw)
                    }
                },
                legend: { position: 'top', labels: { boxWidth: 12, font: { size: 11 } } }
            },
            scales: {
                y: {
                    grid: { color: CHART_COLORS.gridLines },
                    ticks: { callback: currencyFormatter, font: { size: 10 } }
                },
                x: {
                    grid: { display: false },
                    ticks: { font: { size: 9 }, maxRotation: 20 }
                }
            }
        }
    });
}

// Chart 5: Order Status Distribution
function renderOrderStatus(data) {
    const ctx = document.getElementById('chartOrderStatus');
    if (!ctx) return;
    destroyIfExists('orderStatus');

    activeCharts['orderStatus'] = new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: data.labels,
            datasets: [{
                data: data.counts,
                backgroundColor: CHART_COLORS.doughnut,
                borderWidth: 2,
                borderColor: '#ffffff'
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            cutout: '68%',
            plugins: {
                legend: { position: 'right', labels: { boxWidth: 10, font: { size: 11 } } },
                tooltip: {
                    callbacks: {
                        label: (ctx) => ` ${ctx.label}: ${ctx.raw} orders`
                    }
                }
            }
        }
    });
}

// Chart 6: Target vs Actual Revenue
function renderTargetVsActual(data) {
    const ctx = document.getElementById('chartTargetVsActual');
    if (!ctx) return;
    destroyIfExists('targetVsActual');

    activeCharts['targetVsActual'] = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: data.labels,
            datasets: [
                {
                    type: 'line',
                    label: 'Monthly Target',
                    data: data.targets,
                    borderColor: CHART_COLORS.amber,
                    borderWidth: 2.5,
                    borderDash: [5, 5],
                    pointRadius: 4,
                    fill: false
                },
                {
                    type: 'bar',
                    label: 'Actual Revenue',
                    data: data.actuals,
                    backgroundColor: CHART_COLORS.primary,
                    borderRadius: 4
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                tooltip: {
                    callbacks: {
                        label: (ctx) => ctx.dataset.label + ': ' + currencyFormatter(ctx.raw)
                    }
                },
                legend: { position: 'top', labels: { boxWidth: 12, font: { size: 11 } } }
            },
            scales: {
                y: {
                    grid: { color: CHART_COLORS.gridLines },
                    ticks: { callback: currencyFormatter, font: { size: 10 } }
                },
                x: {
                    grid: { display: false },
                    ticks: { font: { size: 10 } }
                }
            }
        }
    });
}

// Chart 7: Customer Revenue Contribution
function renderCustomerContribution(data) {
    const ctx = document.getElementById('chartCustomerContrib');
    if (!ctx) return;
    destroyIfExists('customerContrib');

    activeCharts['customerContrib'] = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: data.labels,
            datasets: [{
                label: 'Total Revenue Generated',
                data: data.spent,
                backgroundColor: CHART_COLORS.primary,
                borderRadius: 4
            }]
        },
        options: {
            indexAxis: 'y',
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                tooltip: {
                    callbacks: {
                        label: (ctx) => 'Revenue: ' + currencyFormatter(ctx.raw)
                    }
                },
                legend: { display: false }
            },
            scales: {
                x: {
                    grid: { color: CHART_COLORS.gridLines },
                    ticks: { callback: currencyFormatter, font: { size: 10 } }
                },
                y: {
                    grid: { display: false },
                    ticks: { font: { size: 10 } }
                }
            }
        }
    });
}

// Chart 8: Revenue Growth Series
function renderRevenueGrowth(data) {
    const ctx = document.getElementById('chartRevenueGrowth');
    if (!ctx) return;
    destroyIfExists('revenueGrowth');

    activeCharts['revenueGrowth'] = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: data.labels,
            datasets: [
                {
                    type: 'line',
                    label: 'MoM Growth Rate (%)',
                    data: data.growth_rate,
                    borderColor: CHART_COLORS.emerald,
                    backgroundColor: CHART_COLORS.emerald,
                    borderWidth: 2,
                    yAxisID: 'y1',
                    pointRadius: 3
                },
                {
                    type: 'bar',
                    label: 'Monthly Net Revenue',
                    data: data.revenue,
                    backgroundColor: CHART_COLORS.cogsLight,
                    borderColor: CHART_COLORS.cogs,
                    borderWidth: 1,
                    yAxisID: 'y',
                    borderRadius: 4
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                tooltip: {
                    callbacks: {
                        label: function (ctx) {
                            if (ctx.dataset.yAxisID === 'y1') {
                                return ` Growth: ${ctx.raw}%`;
                            }
                            return ` Revenue: ${currencyFormatter(ctx.raw)}`;
                        }
                    }
                },
                legend: { position: 'top', labels: { boxWidth: 12, font: { size: 11 } } }
            },
            scales: {
                y: {
                    position: 'left',
                    grid: { color: CHART_COLORS.gridLines },
                    ticks: { callback: currencyFormatter, font: { size: 10 } }
                },
                y1: {
                    position: 'right',
                    grid: { display: false },
                    ticks: { callback: (val) => val + '%', font: { size: 10 } }
                },
                x: {
                    grid: { display: false },
                    ticks: { font: { size: 10 } }
                }
            }
        }
    });
}
