function addBlock(type) {
    const container = document.querySelector(`.${type}-list`);
    
    const lastBlock = container.lastElementChild;
    if (lastBlock) {
        const inputs = lastBlock.querySelectorAll('input[required], select[required], textarea[required]');
        let allFilled = true;
        inputs.forEach(input => {
            if (!input.value.trim()) allFilled = false;
        });
        if (!allFilled) {
            alert("Please fill in all required fields before adding a new section.");
            return;
        }
    }

    const template = document.getElementById(`${type}-template`);
    if (template) {
        const clone = template.content.cloneNode(true);
        container.appendChild(clone);
    } else {
        console.error("Template not found for type: " + type);
    }
}

function removeBlock(btn) {
    btn.closest('.block-section').remove();
}

function toggleEducation() {
    const checkbox = document.getElementById('graduatedCheck');
    const container = document.querySelector('.education-list');
    const addBtn = document.getElementById('btn-add-edu');

    if (checkbox.checked) {
        addBtn.classList.remove('d-none');
        if (container.children.length === 0) {
            addBlock('education');
        }
    } else {
        addBtn.classList.add('d-none');
        container.innerHTML = '';
    }
}

function submitCV() {
    const form = document.getElementById('cvForm');
    const gradCheck = document.getElementById('graduatedCheck');
    const eduList = document.querySelector('.education-list');
    
    if (gradCheck && gradCheck.checked && eduList.children.length === 0) {
        alert("You selected 'Graduated'. Please add at least one education entry.");
        return;
    }

    if (!form.checkValidity()) {
        form.reportValidity();
        return;
    }

    let msg = "Are you sure you want to submit this CV?";
    if (typeof isEdit !== 'undefined' && isEdit) {
        msg = "Are you sure you want to update your CV?";
    }

    if (confirm(msg)) {
        form.submit();
    }
}

async function analyzeCV() {
    const btn = document.getElementById('analyzeBtn');
    if (btn) {
        btn.innerText = "Analyzing...";
        btn.disabled = true;
    }

    try {
        // 1. Get the profile text
        const cvText = document.querySelector('textarea[name="profile"]').value;
        
        // 2. Call ML Backend (Port 5000)
        const mlResponse = await fetch('http://127.0.0.1:5000/api/analyze', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ cv_text: cvText })
        });
        const mlData = await mlResponse.json();
        
        if (mlData.status === "success") {
            // 3. Send results to Frontend Database (Port 8000)
            // Note: We use relative path '/save_analysis' which automatically goes to port 8000
            const saveResponse = await fetch('/save_analysis', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    jobs: mlData.jobs,
                    missing_skills: mlData.missing_skills,
                    recommendations: mlData.recommendations
                })
            });

            const saveData = await saveResponse.json();

            if (saveData.status === "saved") {
                alert("Analysis Saved! View your Top Matches.");
                window.location.href = "/jobs"; // Redirect to the jobs list
            }
        } else {
            alert("Analysis failed: " + mlData.error);
        }

    } catch (error) {
        console.error("Error:", error);
        alert("Connection Error. Ensure both Frontend (8000) and Backend (5000) are running.");
    } finally {
        if (btn) {
            btn.innerText = "Analyze CV";
            btn.disabled = false;
        }
    }
}
