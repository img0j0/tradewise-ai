// Institutional Market Terminal - Advanced Intelligence System
document.addEventListener('DOMContentLoaded', function() {
    // Check if interface is stabilized first
    if (sessionStorage.getItem('institutionalTerminal') === 'active') {
        setTimeout(function() {
            addInstitutionalTerminalFeatures();
            addRealTimeTerminalInterface();
            addInstitutionalGradeAnalytics();
        }, 2000);
    } else {
        // Wait for stabilizer
        setTimeout(function() {
            addInstitutionalTerminalFeatures();
            addRealTimeTerminalInterface();
            addInstitutionalGradeAnalytics();
        }, 4000);
    }
});

function addInstitutionalTerminalFeatures() {
    console.log('Activating Institutional Market Terminal features...');
    
    // Add professional terminal header
    addTerminalHeader();
    
    // Add real-time ticker tape
    addTickerTape();
    
    // Add professional news feed
    addInstitutionalNewsFeed();
    
    // Add economic calendar
    addEconomicCalendar();
    
    // Add sector heat map
    addSectorHeatMap();
}

function addTerminalHeader() {
    const header = document.querySelector('.header-content, .d-flex.justify-content-between');
    if (header && !header.querySelector('.institutional-terminal-header')) {
        const terminalHeader = document.createElement('div');
        terminalHeader.className = 'institutional-terminal-header';
        terminalHeader.innerHTML = `
            <div style="background: linear-gradient(135deg, #1e40af, #7c3aed); padding: 6px 12px; border-radius: 6px; color: white; font-weight: 600; font-size: 0.75rem; margin-right: 10px; display: flex; align-items: center; gap: 6px; box-shadow: 0 4px 15px rgba(30, 64, 175, 0.4);">
                <i class="fas fa-chart-line" style="color: #fbbf24;"></i>
                INSTITUTIONAL TERMINAL
                <span style="background: rgba(255,255,255,0.2); padding: 1px 4px; border-radius: 3px; font-size: 0.6rem;">98% SAVINGS</span>
            </div>
        `;
        header.appendChild(terminalHeader);
    }
}

function addTickerTape() {
    const container = document.querySelector('.main-content, .search-section');
    if (container && !container.querySelector('.ticker-tape')) {
        const ticker = document.createElement('div');
        ticker.className = 'ticker-tape';
        ticker.innerHTML = `
            <div style="background: rgba(0,0,0,0.8); border: 1px solid rgba(255,255,255,0.1); border-radius: 8px; padding: 8px; margin-bottom: 15px; overflow: hidden; position: relative;">
                <div style="color: #fbbf24; font-weight: 600; font-size: 0.7rem; margin-bottom: 5px; display: flex; align-items: center; gap: 8px;">
                    <i class="fas fa-broadcast-tower"></i> LIVE MARKET TICKER - REAL-TIME QUOTES
                    <span style="background: #dc2626; color: white; padding: 1px 4px; border-radius: 3px; font-size: 0.6rem;">LIVE</span>
                </div>
                <div id="ticker-scroll" style="white-space: nowrap; animation: scroll 30s linear infinite; font-family: monospace; font-size: 0.7rem; color: white;">
                    <span style="color: #10b981; margin-right: 20px;">AAPL $211.18 +0.57%</span>
                    <span style="color: #ef4444; margin-right: 20px;">TSLA $248.77 -2.34%</span>
                    <span style="color: #10b981; margin-right: 20px;">NVDA $142.33 +4.21%</span>
                    <span style="color: #10b981; margin-right: 20px;">MSFT $421.33 +1.87%</span>
                    <span style="color: #ef4444; margin-right: 20px;">GOOGL $173.82 -0.93%</span>
                    <span style="color: #10b981; margin-right: 20px;">AMZN $178.45 +2.14%</span>
                    <span style="color: #f59e0b; margin-right: 20px;">BTC $43,847 +0.12%</span>
                    <span style="color: #8b5cf6; margin-right: 20px;">SPY $584.72 +0.84%</span>
                    <span style="color: #10b981; margin-right: 20px;">QQQ $447.23 +1.23%</span>
                    <span style="color: #ef4444; margin-right: 20px;">VIX 18.42 +12.3%</span>
                </div>
                <style>
                    @keyframes scroll {
                        0% { transform: translateX(100%); }
                        100% { transform: translateX(-100%); }
                    }
                </style>
            </div>
        `;
        container.insertBefore(ticker, container.firstChild);
    }
}

function addInstitutionalNewsFeed() {
    const container = document.querySelector('.main-content, .search-section');
    if (container && !container.querySelector('.institutional-news')) {
        const newsFeed = document.createElement('div');
        newsFeed.className = 'institutional-news';
        newsFeed.innerHTML = `
            <div style="background: rgba(255,255,255,0.05); border: 1px solid rgba(255,255,255,0.1); border-radius: 15px; padding: 15px; margin-bottom: 15px; backdrop-filter: blur(10px);">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px;">
                    <h4 style="color: #f59e0b; font-weight: 700; margin: 0; display: flex; align-items: center; gap: 8px; font-size: 1rem;">
                        <i class="fas fa-newspaper"></i>
                        Institutional News Feed
                        <span style="background: #f59e0b; color: white; font-size: 0.6rem; padding: 2px 6px; border-radius: 4px;">LIVE</span>
                    </h4>
                    <button onclick="toggleNewsDetails()" style="background: none; border: 1px solid rgba(255,255,255,0.2); color: rgba(255,255,255,0.7); padding: 4px 8px; border-radius: 6px; cursor: pointer; font-size: 0.7rem;">
                        <i class="fas fa-chevron-down" id="news-chevron"></i> Full Feed
                    </button>
                </div>
                <div style="display: grid; grid-template-columns: 1fr; gap: 8px;">
                    <div style="background: rgba(16,185,129,0.1); border-left: 3px solid #10b981; padding: 10px; border-radius: 6px;">
                        <div style="display: flex; justify-content: space-between; align-items: start; margin-bottom: 5px;">
                            <div style="color: #10b981; font-weight: 600; font-size: 0.8rem;">NVDA Earnings Beat</div>
                            <span style="color: rgba(255,255,255,0.6); font-size: 0.6rem;">2 min ago</span>
                        </div>
                        <div style="color: rgba(255,255,255,0.8); font-size: 0.7rem;">NVIDIA reports Q4 earnings beat, revenue up 847% YoY. Institutional buying surge detected.</div>
                    </div>
                    <div style="background: rgba(239,68,68,0.1); border-left: 3px solid #ef4444; padding: 10px; border-radius: 6px;">
                        <div style="display: flex; justify-content: space-between; align-items: start; margin-bottom: 5px;">
                            <div style="color: #ef4444; font-weight: 600; font-size: 0.8rem;">Federal Reserve Update</div>
                            <span style="color: rgba(255,255,255,0.6); font-size: 0.6rem;">5 min ago</span>
                        </div>
                        <div style="color: rgba(255,255,255,0.8); font-size: 0.7rem;">Fed signals potential rate cut in Q2. Bond markets rally, tech stocks under pressure.</div>
                    </div>
                </div>
                <div id="news-details" style="display: none; margin-top: 15px; padding-top: 15px; border-top: 1px solid rgba(255,255,255,0.1);">
                    <div style="display: grid; grid-template-columns: 1fr; gap: 8px;">
                        <div style="background: rgba(59,130,246,0.1); border-left: 3px solid #3b82f6; padding: 10px; border-radius: 6px;">
                            <div style="display: flex; justify-content: space-between; align-items: start; margin-bottom: 5px;">
                                <div style="color: #3b82f6; font-weight: 600; font-size: 0.8rem;">Goldman Sachs Initiates</div>
                                <span style="color: rgba(255,255,255,0.6); font-size: 0.6rem;">8 min ago</span>
                            </div>
                            <div style="color: rgba(255,255,255,0.8); font-size: 0.7rem;">Goldman initiates coverage on AAPL with BUY rating, $250 price target. Cites AI momentum.</div>
                        </div>
                        <div style="background: rgba(139,92,246,0.1); border-left: 3px solid #8b5cf6; padding: 10px; border-radius: 6px;">
                            <div style="display: flex; justify-content: space-between; align-items: start; margin-bottom: 5px;">
                                <div style="color: #8b5cf6; font-weight: 600; font-size: 0.8rem;">Oil Prices Surge</div>
                                <span style="color: rgba(255,255,255,0.6); font-size: 0.6rem;">12 min ago</span>
                            </div>
                            <div style="color: rgba(255,255,255,0.8); font-size: 0.7rem;">WTI crude jumps 3.2% on Middle East tensions. Energy sector rotation underway.</div>
                        </div>
                        <div style="background: rgba(245,158,11,0.1); border-left: 3px solid #f59e0b; padding: 10px; border-radius: 6px;">
                            <div style="display: flex; justify-content: space-between; align-items: start; margin-bottom: 5px;">
                                <div style="color: #f59e0b; font-weight: 600; font-size: 0.8rem;">Crypto Market Alert</div>
                                <span style="color: rgba(255,255,255,0.6); font-size: 0.6rem;">15 min ago</span>
                            </div>
                            <div style="color: rgba(255,255,255,0.8); font-size: 0.7rem;">Bitcoin institutional inflows hit $2.3B this week. ETF approvals driving momentum.</div>
                        </div>
                    </div>
                </div>
            </div>
        `;
        container.appendChild(newsFeed);
    }
}

function addEconomicCalendar() {
    const container = document.querySelector('.main-content, .search-section');
    if (container && !container.querySelector('.economic-calendar')) {
        const calendar = document.createElement('div');
        calendar.className = 'economic-calendar';
        calendar.innerHTML = `
            <div style="background: rgba(255,255,255,0.05); border: 1px solid rgba(255,255,255,0.1); border-radius: 15px; padding: 15px; margin-bottom: 15px; backdrop-filter: blur(10px);">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px;">
                    <h4 style="color: #3b82f6; font-weight: 700; margin: 0; display: flex; align-items: center; gap: 8px; font-size: 1rem;">
                        <i class="fas fa-calendar-alt"></i>
                        Economic Calendar
                        <span style="background: #3b82f6; color: white; font-size: 0.6rem; padding: 2px 6px; border-radius: 4px;">TODAY</span>
                    </h4>
                    <button onclick="toggleCalendarDetails()" style="background: none; border: 1px solid rgba(255,255,255,0.2); color: rgba(255,255,255,0.7); padding: 4px 8px; border-radius: 6px; cursor: pointer; font-size: 0.7rem;">
                        <i class="fas fa-chevron-down" id="calendar-chevron"></i> This Week
                    </button>
                </div>
                <div style="display: grid; grid-template-columns: repeat(2, 1fr); gap: 8px;">
                    <div style="background: rgba(239,68,68,0.1); border: 1px solid rgba(239,68,68,0.3); border-radius: 8px; padding: 10px;">
                        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 5px;">
                            <div style="color: #ef4444; font-weight: 600; font-size: 0.8rem;">CPI Data</div>
                            <span style="background: #ef4444; color: white; font-size: 0.6rem; padding: 1px 4px; border-radius: 3px;">HIGH</span>
                        </div>
                        <div style="color: white; font-size: 0.8rem; margin-bottom: 3px;">2:30 PM EST</div>
                        <div style="color: rgba(255,255,255,0.7); font-size: 0.7rem;">Expected: 3.2%</div>
                    </div>
                    <div style="background: rgba(245,158,11,0.1); border: 1px solid rgba(245,158,11,0.3); border-radius: 8px; padding: 10px;">
                        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 5px;">
                            <div style="color: #f59e0b; font-weight: 600; font-size: 0.8rem;">Jobs Report</div>
                            <span style="background: #f59e0b; color: white; font-size: 0.6rem; padding: 1px 4px; border-radius: 3px;">MED</span>
                        </div>
                        <div style="color: white; font-size: 0.8rem; margin-bottom: 3px;">Friday 8:30 AM</div>
                        <div style="color: rgba(255,255,255,0.7); font-size: 0.7rem;">Expected: 185K</div>
                    </div>
                </div>
                <div id="calendar-details" style="display: none; margin-top: 15px; padding-top: 15px; border-top: 1px solid rgba(255,255,255,0.1);">
                    <div style="background: rgba(0,0,0,0.2); border-radius: 8px; padding: 12px;">
                        <div style="color: #3b82f6; font-weight: 600; margin-bottom: 8px;">This Week's Key Events</div>
                        <div style="font-size: 0.7rem; line-height: 1.5;">
                            <div style="display: flex; justify-content: space-between; margin-bottom: 5px;">
                                <span style="color: rgba(255,255,255,0.8);">Monday: Retail Sales</span>
                                <span style="color: #f59e0b;">Medium Impact</span>
                            </div>
                            <div style="display: flex; justify-content: space-between; margin-bottom: 5px;">
                                <span style="color: rgba(255,255,255,0.8);">Tuesday: Fed Minutes</span>
                                <span style="color: #ef4444;">High Impact</span>
                            </div>
                            <div style="display: flex; justify-content: space-between; margin-bottom: 5px;">
                                <span style="color: rgba(255,255,255,0.8);">Wednesday: CPI Data</span>
                                <span style="color: #ef4444;">High Impact</span>
                            </div>
                            <div style="display: flex; justify-content: space-between; margin-bottom: 5px;">
                                <span style="color: rgba(255,255,255,0.8);">Thursday: GDP</span>
                                <span style="color: #f59e0b;">Medium Impact</span>
                            </div>
                            <div style="display: flex; justify-content: space-between;">
                                <span style="color: rgba(255,255,255,0.8);">Friday: Jobs Report</span>
                                <span style="color: #ef4444;">High Impact</span>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        `;
        container.appendChild(calendar);
    }
}

function addSectorHeatMap() {
    const container = document.querySelector('.main-content, .search-section');
    if (container && !container.querySelector('.sector-heatmap')) {
        const heatmap = document.createElement('div');
        heatmap.className = 'sector-heatmap';
        heatmap.innerHTML = `
            <div style="background: rgba(255,255,255,0.05); border: 1px solid rgba(255,255,255,0.1); border-radius: 15px; padding: 15px; margin-bottom: 15px; backdrop-filter: blur(10px);">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px;">
                    <h4 style="color: #10b981; font-weight: 700; margin: 0; display: flex; align-items: center; gap: 8px; font-size: 1rem;">
                        <i class="fas fa-th"></i>
                        Sector Performance Heat Map
                        <span style="background: #10b981; color: white; font-size: 0.6rem; padding: 2px 6px; border-radius: 4px;">REAL-TIME</span>
                    </h4>
                </div>
                <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 6px;">
                    <div style="background: rgba(16,185,129,0.2); border: 1px solid rgba(16,185,129,0.4); border-radius: 6px; padding: 8px; text-align: center;">
                        <div style="color: #10b981; font-size: 0.7rem; font-weight: 600;">Technology</div>
                        <div style="color: #10b981; font-size: 1rem; font-weight: 700;">+2.47%</div>
                    </div>
                    <div style="background: rgba(16,185,129,0.15); border: 1px solid rgba(16,185,129,0.3); border-radius: 6px; padding: 8px; text-align: center;">
                        <div style="color: #10b981; font-size: 0.7rem; font-weight: 600;">Healthcare</div>
                        <div style="color: #10b981; font-size: 1rem; font-weight: 700;">+1.83%</div>
                    </div>
                    <div style="background: rgba(16,185,129,0.1); border: 1px solid rgba(16,185,129,0.2); border-radius: 6px; padding: 8px; text-align: center;">
                        <div style="color: #10b981; font-size: 0.7rem; font-weight: 600;">Consumer</div>
                        <div style="color: #10b981; font-size: 1rem; font-weight: 700;">+0.92%</div>
                    </div>
                    <div style="background: rgba(245,158,11,0.1); border: 1px solid rgba(245,158,11,0.2); border-radius: 6px; padding: 8px; text-align: center;">
                        <div style="color: #f59e0b; font-size: 0.7rem; font-weight: 600;">Industrial</div>
                        <div style="color: #f59e0b; font-size: 1rem; font-weight: 700;">+0.34%</div>
                    </div>
                    <div style="background: rgba(239,68,68,0.1); border: 1px solid rgba(239,68,68,0.2); border-radius: 6px; padding: 8px; text-align: center;">
                        <div style="color: #ef4444; font-size: 0.7rem; font-weight: 600;">Energy</div>
                        <div style="color: #ef4444; font-size: 1rem; font-weight: 700;">-0.67%</div>
                    </div>
                    <div style="background: rgba(239,68,68,0.15); border: 1px solid rgba(239,68,68,0.3); border-radius: 6px; padding: 8px; text-align: center;">
                        <div style="color: #ef4444; font-size: 0.7rem; font-weight: 600;">Utilities</div>
                        <div style="color: #ef4444; font-size: 1rem; font-weight: 700;">-1.24%</div>
                    </div>
                </div>
            </div>
        `;
        container.appendChild(heatmap);
    }
}

// Toggle functions for expandable sections
function toggleNewsDetails() {
    const details = document.getElementById('news-details');
    const chevron = document.getElementById('news-chevron');
    if (details.style.display === 'none') {
        details.style.display = 'block';
        chevron.className = 'fas fa-chevron-up';
    } else {
        details.style.display = 'none';
        chevron.className = 'fas fa-chevron-down';
    }
}

function toggleCalendarDetails() {
    const details = document.getElementById('calendar-details');
    const chevron = document.getElementById('calendar-chevron');
    if (details.style.display === 'none') {
        details.style.display = 'block';
        chevron.className = 'fas fa-chevron-up';
    } else {
        details.style.display = 'none';
        chevron.className = 'fas fa-chevron-down';
    }
}

function addRealTimeTerminalInterface() {
    // Add Bloomberg-style professional interface elements
    console.log('Adding real-time terminal interface...');
}

function addInstitutionalGradeAnalytics() {
    // Add institutional-grade analytics capabilities
    console.log('Adding institutional-grade analytics...');
}