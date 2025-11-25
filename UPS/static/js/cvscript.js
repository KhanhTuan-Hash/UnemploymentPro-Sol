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
