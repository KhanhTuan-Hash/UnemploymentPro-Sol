const ul = document.querySelector(".content ul");
const input = document.getElementById("tags-input");
const countNumb = document.querySelector(".details span");

let tags = [];
let maxTags = 10;

countTag();

function getTags() {
    return tags;
}

function countTag() {
    input.focus();
    countNumb.innerText = maxTags - tags.length;
}

function createTag() {
    ul.querySelectorAll("li").forEach(li => li.remove());
    console.log(tags);
    tags.slice().reverse().forEach(tag =>{
        let liTag = `<li>${tag} <i class="bi bi-x-circle-fill" onclick="removeTag(this, '${tag}')"></i></li>`;
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
    if (e.keyCode === 13) {
        e.preventDefault(); 
        let tag = e.target.value.replace(/\s+/g, ' ').trim();
        if (tag.length > 0 && tags.length < maxTags) {
            tag.split(',').forEach(t =>{
                let currentTag = t.trim();
                if (currentTag.length > 0 && !tags.includes(currentTag) && tags.length < maxTags) {
                    tags.push(currentTag);
                }
            });
            createTag();
        }
        
        e.target.value = "";
    }
}

input.addEventListener("keydown", addTag);

const removeBtn = document.querySelector(".remove-all-btn");
removeBtn.addEventListener("click", () =>{
    tags.length = 0;
    ul.querySelectorAll("li").forEach(li => li.remove());
    countTag();
});