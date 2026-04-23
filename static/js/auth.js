
// 1. Update the UI Lists (Shared by Admin & User)
async function updateUI() {
    try {
        console.log("Attempting to fetch results...");
        const res = await fetch('/api/results');
        const data = await res.json();
        console.log("Server Response:", data);

        const categories = ['Silver', 'Gold', 'Grand'];
        
        categories.forEach(cat => {
            const listId = `${cat.toLowerCase()}-list`;
            const container = document.getElementById(listId);
            
            if (container) {
                container.innerHTML = ""; // Clear old content
                
                if (data[cat] && data[cat].length > 0) {
                    data[cat].forEach(winner => {
                        container.innerHTML += `
                            <div class="ticket-tag">
                                <span>Ticket: <b>${winner.ticket}</b></span>
                                <span class="prize-amt">₹${winner.prize.toLocaleString()}</span>
                            </div>`;
                    });
                } else {
                    container.innerHTML = `<p style="text-align:center; color:gray; font-size:12px;">No winners yet</p>`;
                }
            } else {
                console.warn(`HTML element with ID: ${listId} not found on this page.`);
            }
        });
    } catch (err) {
        console.error("Fetch Error:", err);
    }
}

// 2. Admin Draw Trigger
async function triggerDraw(cat) {
    try {
        const res = await fetch('/api/generate', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({category: cat})
        });
        
        const data = await res.json();
        
        if(data.status === "success") {
            Swal.fire({
                title: 'Draw Finalized',
                text: data.message,
                icon: 'success',
                background: '#1e293b',
                color: '#f1f5f9',
                confirmButtonColor: '#6366f1'
            });
            updateUI(); // Refresh numbers immediately
        }
    } catch (err) {
        console.error("Draw Error:", err);
    }
}

// 3. Login Logic (Admin & User)
async function handleLogin(role) {
    const uid = document.getElementById('uid').value.trim();
    const pwd = document.getElementById('pwd').value.trim();

    if (!uid || !pwd) {
        alert("⚠️ Please enter both fields.");
        return;
    }

    try {
        const response = await fetch('/login', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ id: uid, pass: pwd, role: role })
        });

        const data = await response.json();

        if (response.ok && data.status === "success") {
            window.location.href = data.redirect;
        } else {
            alert("❌ Login Error: " + data.message);
        }
    } catch (error) {
        console.error("Login Fetch Error:", error);
        alert("🚨 Connection failed. Is your terminal running?");
    }
}

// 4. User Ticket Search
async function checkMyTicket() {
    console.log("Search button clicked!");
    
    const inputField = document.getElementById('ticket-search');
    if (!inputField) {
        console.error("Could not find input field with ID 'ticket-search'");
        return;
    }

    const input = inputField.value.trim();
    if (!input) return alert("Please enter a ticket number");

    try {
        const res = await fetch('/api/results');
        const data = await res.json();

        let won = false;
        let prizeDetail = "";

        for (let cat in data) {
            data[cat].forEach(winner => {
                if (String(winner.ticket) === String(input)) {
                    won = true;
                    prizeDetail = `${cat} Class - ₹${winner.prize.toLocaleString()}`;
                }
            });
        }

        if (won) {
            Swal.fire({ 
                title: '🎉 Winner!', 
                text: `Ticket #${input} won the ${prizeDetail}!`, 
                icon: 'success',
                background: '#0f172a',
                color: '#fff'
            });
        } else {
            Swal.fire({ 
                title: 'No Luck', 
                text: 'Ticket not found in current winners.', 
                icon: 'error',
                background: '#0f172a',
                color: '#fff'
            });
        }
    } catch (err) {
        console.error("Check Error:", err);
    }
}

// Auto-load lists on page open
window.onload = updateUI;