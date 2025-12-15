/**
 * AngyOne Decision Engine
 * Logic: 3 Steps (Category -> Team -> Budget) => Recommendation
 */

const toolDatabase = [
    // MARKETING / EMAIL
    { id: "brevo", name: "Brevo", cat: "marketing", team: "solo", budget: "free", reason: "Unbeatable Free Plan (Unlimited Contacts).", link: "brevo/" },
    { id: "brevo", name: "Brevo", cat: "marketing", team: "startup", budget: "cheap", reason: "Cheapest scaling costs.", link: "brevo/" },
    { id: "hubspot", name: "HubSpot", cat: "marketing", team: "enterprise", budget: "premium", reason: "The gold standard for large teams.", link: "#" },

    // PRODUCTIVITY / PROJECT
    { id: "notion", name: "Notion", cat: "productivity", team: "solo", budget: "free", reason: "Best for building your own workspace.", link: "#" },
    { id: "linear", name: "Linear", cat: "productivity", team: "startup", budget: "cheap", reason: "Fastest for software teams.", link: "#" },
    { id: "linear", name: "Linear", cat: "productivity", team: "enterprise", budget: "premium", reason: "Scales beautifully for engineering.", link: "#" },

    // CRM
    { id: "brevo_crm", name: "Brevo CRM", cat: "crm", team: "solo", budget: "free", reason: "It's built-in and free.", link: "brevo/" },
    { id: "hubspot_crm", name: "HubSpot CRM", cat: "crm", team: "startup", budget: "free", reason: "Best free CRM features.", link: "#" },
    { id: "salesforce", name: "Salesforce", cat: "crm", team: "enterprise", budget: "premium", reason: "Industry leader for sales teams.", link: "#" },
];

let currentStep = 0;
let userAnswers = {};

const questions = [
    {
        id: "cat",
        question: "What are you looking for?",
        options: [
            { label: "Marketing / Email", value: "marketing", icon: "📧" },
            { label: "Project Mgmt", value: "productivity", icon: "✅" },
            { label: "CRM", value: "crm", icon: "🤝" }
        ]
    },
    {
        id: "team",
        question: "How big is your team?",
        options: [
            { label: "Just Me (Solo)", value: "solo", icon: "👤" },
            { label: "Startup (1-20)", value: "startup", icon: "🚀" },
            { label: "Enterprise (20+)", value: "enterprise", icon: "🏢" }
        ]
    },
    {
        id: "budget",
        question: "What's your budget?",
        options: [
            { label: "Free Forever", value: "free", icon: "🎁" },
            { label: "Cheap (<$20)", value: "cheap", icon: "💵" },
            { label: "Premium / No Limit", value: "premium", icon: "💎" }
        ]
    }
];

function initDecisionEngine() {
    const container = document.getElementById('decision-engine-container');
    if (!container) return;
    renderStep();
}

function renderStep() {
    const container = document.getElementById('decision-engine-container');
    const q = questions[currentStep];

    // Progress Bar Calculation
    const progress = ((currentStep) / questions.length) * 100;

    let html = `
        <div class="quiz-card">
            <div class="quiz-progress">
                <div class="quiz-progress-bar" style="width: ${progress}%"></div>
            </div>
            <h3 class="quiz-question">${q.question}</h3>
            <div class="quiz-options-grid">
    `;

    q.options.forEach(opt => {
        html += `
            <button class="quiz-btn" onclick="handleAnswer('${q.id}', '${opt.value}')">
                <span class="quiz-icon">${opt.icon}</span>
                <span class="quiz-label">${opt.label}</span>
            </button>
        `;
    });

    html += `</div></div>`;
    container.innerHTML = html;
}

function handleAnswer(key, value) {
    userAnswers[key] = value;
    currentStep++;

    if (currentStep < questions.length) {
        renderStep();
    } else {
        showResult();
    }
}

function showResult() {
    const container = document.getElementById('decision-engine-container');

    // Find Match
    const match = toolDatabase.find(t =>
        t.cat === userAnswers.cat &&
        t.team === userAnswers.team &&
        t.budget === userAnswers.budget
    );

    // Fallback if no exact match (Loose match on Category + Team)
    const fallback = toolDatabase.find(t => t.cat === userAnswers.cat && t.team === userAnswers.team) || toolDatabase[0];

    const result = match || fallback;

    container.innerHTML = `
        <div class="quiz-card result-card">
            <div class="result-header">
                <span class="result-label">We Recommend</span>
                <h2>${result.name}</h2>
            </div>
            <p class="result-reason">"${result.reason}"</p>
            <div class="result-actions">
                <a href="${result.link}" class="btn btn-primary">Try It Now</a>
                <button class="btn btn-text" onclick="resetQuiz()">Start Over</button>
            </div>
        </div>
    `;
}

function resetQuiz() {
    currentStep = 0;
    userAnswers = {};
    renderStep();
}

// Auto-init if script is loaded
document.addEventListener('DOMContentLoaded', initDecisionEngine);
