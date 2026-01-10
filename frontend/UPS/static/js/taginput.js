const ul = document.querySelector(".content ul");
const input = document.getElementById("tags-input");
const countNumb = document.querySelector(".details span");
const hiddenTagInput = document.getElementById("hiddentags");

let maxTags = 10;
let tags = [];

if (hiddenTagInput && hiddenTagInput.value) {
    let existingTags = hiddenTagInput.value.split('-');
    existingTags.forEach(tag => {
        if (tag.trim() !== '') {
            tags.push(tag.trim());
        }
    });
}

countTag();
createTag();

function countTag() {
    if (input) input.focus();
    if (countNumb) countNumb.innerText = maxTags - tags.length;
}

function createTag() {
    if (!ul) return;
    ul.querySelectorAll("li").forEach(li => li.remove());
    
    tags.slice().reverse().forEach(tag => {
        let liTag = `<li>${tag} <i class="bi bi-x" onclick="removeTag(this, '${tag}')"></i></li>`;
        ul.insertAdjacentHTML("afterbegin", liTag);
    });
    countTag();
}

function removeTag(element, tag) {
    let index = tags.indexOf(tag);
    if (index > -1) {
        tags.splice(index, 1);
    }
    element.parentElement.remove();
    countTag();
}

function addTag(e) {
    if (e.key == "Enter") {
        e.preventDefault();
        let tag = e.target.value.replace(/\s+/g, ' ').trim();
        
        if (tag.length > 0 && !tags.includes(tag)) {
            if (tags.length < maxTags) {
                tag.split(',').forEach(t => {
                    let currentTag = t.trim();
                    if (currentTag && !tags.includes(currentTag) && tags.length < maxTags) {
                        tags.push(currentTag);
                    }
                });
                createTag();
            }
        }
        e.target.value = "";
    }
}

if (input) {
    input.addEventListener("keyup", addTag);
}

const removeBtn = document.querySelector(".remove-all-btn");
if (removeBtn) {
    removeBtn.addEventListener("click", () => {
        tags.length = 0;
        ul.querySelectorAll("li").forEach(li => li.remove());
        countTag();
    });
}

function submitJob() {
    if (hiddenTagInput) {
        hiddenTagInput.value = tags.join("-");
    }
    
    if (tags.length === 0) {
        alert("Please enter at least one tag!");
        return;
    }
    
    if (confirm("Confirm save?")) {
        document.getElementById("form-job").submit();
    }
}