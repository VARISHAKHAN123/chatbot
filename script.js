// ---------------------------- CHAT FLOW ----------------------------
function sendMessage() {
    const userInput = document.getElementById('userInput').value;
    const language = document.getElementById('language').value;
    if (userInput.trim() === '') return;

    addMessage(userInput, 'user-message');
    document.getElementById('userInput').value = '';

    fetch('/get', {
        method: 'POST',
        headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
        body: `message=${encodeURIComponent(userInput)}&language=${encodeURIComponent(language)}`
    })
    .then(response => response.json())
    .then(data => {
        addMessage(data.message, 'bot-message');
        speak(data.message, language);

        const symptom = data.symptom?.toLowerCase();
        const symptomsNeedingAge = [...new Set([
            'fever','cold','cough','headache','vomiting','diarrhea',
            'stomach pain','body pain','fatigue','chills','weight loss',
            'appetite loss','night sweats','dizziness','weakness',
            'shortness of breath','unusual thirst','sudden vision changes',
            'confusion or memory loss','muscle or joint pain','chest pain',
            'abdominal pain','back pain','throat pain','leg pain',
            'pelvic pain','painful urination','nausea','constipation',
            'indigestion','heartburn','bloating','blood in stool',
            'dark urine','pale stool','itching','skin rash','jaundice',
            'blisters','dry cracked skin','bruising','sweating',
            'changes in skin color','redness or inflammation',
            'tingling or numbness','seizures','tremors','balance problems',
            'difficulty speaking','slurred speech','weak coordination',
            'memory loss','numbness or paralysis','wheezing',
            'sore throat','blood in cough','chest tightness',
            'frequent urination','blood in urine','hot flashes',
            'unexplained weight gain','increased sweating','hair loss',
            'change in skin or nail texture','depression','anxiety',
            'irritability','sleep problems','mood swings',
            'irregular periods','heavy bleeding','painful intercourse',
            'vaginal discharge','difficulty in erection','testicular pain',
            'changes in libido','heart palpitations','swollen legs or feet',
            'high blood pressure'
        ])];

        if (symptom && symptomsNeedingAge.includes(symptom)) {
            askAge();
        }
    })
    .catch(error => {
        console.error('Error:', error);
        alert('Something went wrong while sending the message.');
    });
}

function addMessage(text, className) {
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${className}`;
    messageDiv.innerText = text;
    document.getElementById('chat-container').appendChild(messageDiv);
    messageDiv.scrollIntoView({ behavior: "smooth" });
}

function askAge() {
    const ageDiv = document.createElement('div');
    ageDiv.className = 'message bot-message';
    ageDiv.innerHTML = `
        Tell me your age please / उम्र बताइये:
        <input type="number" id="ageInput" placeholder="Enter age" style="margin:5px;">
        <button onclick="sendAge()">Submit</button>
    `;
    document.getElementById('chat-container').appendChild(ageDiv);
    ageDiv.scrollIntoView({ behavior: "smooth" });
}

function sendAge() {
    const age = document.getElementById('ageInput').value;
    if (age.trim() === '') return;

    addMessage(`Age: ${age}`, 'user-message');

    fetch('/age', {
        method: 'POST',
        headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
        body: `age=${encodeURIComponent(age)}`
    })
    .then(response => response.json())
    .then(data => {
        addMessage(data.message, 'bot-message');
        speak(data.message, document.getElementById('language').value);

        const consultBtn = document.createElement('button');
        consultBtn.innerText = "Consult a Doctor";
        consultBtn.className = "consult-btn";
        consultBtn.onclick = askLocation;

        const consultDiv = document.createElement('div');
        consultDiv.className = 'message bot-message';
        consultDiv.appendChild(consultBtn);
        document.getElementById('chat-container').appendChild(consultDiv);
        consultDiv.scrollIntoView({ behavior: "smooth" });
    })
    .catch(error => {
        console.error('Error:', error);
        alert('Something went wrong while sending age.');
    });
}

function askLocation() {
    const locationDiv = document.createElement('div');
    locationDiv.className = 'message bot-message';
    locationDiv.innerHTML = `
        कृपया अपना शहर या लोकेशन बताएं:
        <input type="text" id="locationInput" placeholder="Enter city" style="margin:5px;">
        <button onclick="sendLocation()">Submit</button>
    `;
    document.getElementById('chat-container').appendChild(locationDiv);
    locationDiv.scrollIntoView({ behavior: "smooth" });
}

function sendLocation() {
    const location = document.getElementById("locationInput").value;
    if (!location.trim()) {
        alert('Please enter a location.');
        return;
    }

    fetch("/doctor", {
        method: "POST",
        headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
        body: `location=${encodeURIComponent(location)}`
    })
    .then(response => response.json())
    .then(data => {
        displayDoctorCards(data.message);
    })
    .catch(error => {
        console.error('Error:', error);
        alert('Something went wrong while fetching doctor data.');
    });
}

function displayDoctorCards(message) {
    const container = document.getElementById('doctor-list') || document.createElement('div');
    container.id = 'doctor-list';
    container.innerHTML = '';
    const lines = message.split('\n').filter(l => l.trim() !== '');
    lines.forEach(line => {
        const card = document.createElement('div');
        card.className = 'doctor-card';
        card.style.cursor = 'pointer';
        card.style.backgroundColor = '#f0f0f0';
        card.style.padding = '10px';
        card.style.borderRadius = '8px';
        card.style.marginBottom = '10px';
        card.innerText = line;
        card.onclick = () => openMap(line);
        container.appendChild(card);
    });
    document.getElementById('chat-container').appendChild(container);
}

function openMap(location) {
    const mapUrl = "https://www.google.com/maps/search/?api=1&query=" + encodeURIComponent(location);
    window.open(mapUrl, "_blank");
}

// ---------------------------- VOICE ----------------------------
function startListening() {
    const micButton = document.getElementById('micButton');
    micButton.classList.add('recording');

    if (!('webkitSpeechRecognition' in window || 'SpeechRecognition' in window)) {
        alert('Speech recognition not supported in your browser.');
        micButton.classList.remove('recording');
        return;
    }

    const recognition = new (window.SpeechRecognition || window.webkitSpeechRecognition)();
    recognition.lang = document.getElementById('language').value === 'hi' ? 'hi-IN' : 'en-US';
    recognition.interimResults = false;
    recognition.maxAlternatives = 1;

    recognition.start();

    recognition.onresult = function(event) {
        const transcript = event.results[0][0].transcript;
        document.getElementById('userInput').value = transcript;
        sendMessage();
    };

    recognition.onerror = function(event) {
        alert("Voice recognition error: " + event.error);
        micButton.classList.remove('recording');
    };

    recognition.onend = function() {
        micButton.classList.remove('recording');
    };
}

// ---------------------------- SPEECH ----------------------------
function speak(text, language) {
    window.speechSynthesis.cancel();
    const utterance = new SpeechSynthesisUtterance(text);
    utterance.lang = language === 'hi' ? 'hi-IN' : 'en-US';
    utterance.pitch = 1;
    utterance.rate = 1;
    utterance.volume = 1;
    window.speechSynthesis.speak(utterance);
}

// ---------------------------- DIABETES FORM ----------------------------
function predictDiabetes() {
    const data = {
        Pregnancies: parseInt(document.getElementById('pregnancies').value),
        Glucose: parseInt(document.getElementById('glucose').value),
        BloodPressure: parseInt(document.getElementById('bp').value),
        SkinThickness: parseInt(document.getElementById('skin').value),
        Insulin: parseInt(document.getElementById('insulin').value),
        BMI: parseFloat(document.getElementById('bmi').value),
        DiabetesPedigreeFunction: parseFloat(document.getElementById('dpf').value),
        Age: parseInt(document.getElementById('age').value)
    };

    fetch("/chat/diabetes_form", {
        method: "POST",
        headers: {
          "Content-Type": "application/json"
        },
        body: JSON.stringify(data)
      })
      .then(response => response.json())
      .then(result => {
        console.log(result); // For debugging
        document.getElementById("prediction-result").innerText = "Result: " + result.prediction;
      })
      .catch(error => {
        console.error("Error:", error);
      });
      
}
function toggleDiabetesForm() {
    const panel = document.getElementById("diabetes-panel");
    if (panel.style.display === "none" || panel.style.display === "") {
        panel.style.display = "block";
    } else {
        panel.style.display = "none";
    }
}


// ---------------------------- MENTAL HEALTH ----------------------------
document.getElementById('mentalHealthBtn').addEventListener('click', function () {
    const panel = document.getElementById('mental-health-panel');
    panel.style.display = (panel.style.display === 'none' || panel.style.display === '') ? 'block' : 'none';
});

function submitMentalAssessment() {
    const data = {
        stress: document.getElementById('stress-level').value,
        sleep: document.getElementById('sleep-trouble').value,
        need_support: document.getElementById('need-support').value
    };

    fetch('/mental_assessment', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data)
    })
    .then(res => res.json())
    .then(response => {
        alert(response.message || "Thank you! We received your response.");
        document.getElementById('mental-health-panel').style.display = 'none';
    })
    .catch(err => {
        alert("Something went wrong. Please try again.");
        console.error("Assessment Error:", err);
    });
}
