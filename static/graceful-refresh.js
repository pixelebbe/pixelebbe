const image = document.querySelector('.beamer img');
const imageUrl = image.src;

let refreshImage = () => {
    image.src = imageUrl + '?d=' + Date.now()
}

window.addEventListener("load", () => {
    window.setInterval(refreshImage, 1000)
})