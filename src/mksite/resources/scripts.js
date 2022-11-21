function toggleFullscreen(element) {
    if (browserIsFullscreen() && element === getFullscreenElement()) {
        exitFullscreen();
    }
    else {
        enterFullscreen(element);
    }
}

function enterFullscreen(element) {
    if (browserIsFullscreen()) {
        return;
    }
    if (element.requestFullscreen) {
        element.requestFullscreen({ navigationUI: "hide" });
    }
    else if (element.mozRequestFullScreen) {
        element.mozRequestFullScreen({ navigationUI: "hide" });
    }
    else if (element.webkitRequestFullScreen) {
        element.webkitRequestFullScreen();
    }
    else if (element.msRequestFullscreen) {
        element.msRequestFullscreen();
    }
}

function exitFullscreen(){
    if (document.exitFullscreen) {
        document.exitFullscreen();
    }
    else if (document.mozCancelFullScreen) {
        document.mozCancelFullScreen();
    }
    else if (document.webkitCancelFullScreen) {
        document.webkitCancelFullScreen();
    }
    else if (document.msExitFullscreen) {
        document.msExitFullscreen();
    }
}

function onFullscreenChange(callback){
    document.addEventListener("fullscreenchange", (event) => {
                callback(event);
    }, false);

    document.addEventListener("mozfullscreenchange", (event) => {
                callback(event);
    }, false);

    document.addEventListener("webkitfullscreenchange", (event) => {
                callback(event);
    }, false);

    document.addEventListener("msfullscreenchange", (event) => {
                callback(event);
    }, false);
}

function browserIsFullscreen() {
        return document.fullscreenElement != null || document.webkitFullscreenElement != null;
}

function getFullscreenElement() {
    if (document.fullscreenElement != null) {
        return document.fullscreenElement;
    }
    return document.webkitFullscreenElement;
}

let rows;
let container;
let helpButton = document.getElementById("help");
let helpDialog = document.getElementById("help-dialog");
let slideshowButton = document.getElementById("slideshow-button");
let viewingSlides = false;

document.addEventListener("DOMContentLoaded", (event) => {
    rows = document.getElementsByClassName("row");
    container = document.getElementById("fullscreen-container");
    helpButton = document.getElementById("help");
    helpDialog = document.getElementById("help-dialog");
    slideshowButton = document.getElementById("slideshow-button");
});

document.addEventListener("keydown", (event) => {
    if (!viewingSlides) {
        return;
    }
    if (event.key == "ArrowRight") {
        nextSlide();
    }
    if (event.key == "ArrowLeft") {
        previousSlide();
    }
});

function slideShow() {
    container.displaying = 0;
    enterFullscreen(container);
    container.innerHTML = rows[container.displaying].outerHTML;
    fixFSHeights(container)
    viewingSlides = true;
}

function nextSlide() {
    if (container.displaying < rows.length - 2) {
        container.displaying += 1;
        container.innerHTML = rows[container.displaying].outerHTML;
        fixFSHeights(container)
    }
}

function previousSlide() {
    if (container.displaying > 0) {
        container.displaying -= 1;
        container.innerHTML = rows[container.displaying].outerHTML;
        fixFSHeights(container)
    }
}

function exitSlideShow() {
    clearContainer();
    viewingSlides = false;
}

onFullscreenChange((event) => {
    if (!browserIsFullscreen()) {
        exitSlideShow();
    }
});

function clearContainer() {
   container.innerHTML = '';
}

function help() {
    const dialog = document.getElementById("help-dialog");
    dialog.style.display = dialog.style.display == "block" ? "none" : "block";
}

window.onclick = function(event) {
    if (event.target != slideshowButton && viewingSlides) {
        if (event.clientX >= window.innerWidth / 2) {
            nextSlide();
        } else {
            previousSlide()
        }
    }
    else if (event.target != helpButton) {
        helpDialog.style.display = "none";
    }
}

function fixHeights(element) {
    if (element.children.length == 0) {
        return;
    }
    height = element.parentElement.offsetHeight + "px";
    element.style.maxHeight = height;
    for (let i = 0; i < element.children.length; i++) {
        fixHeights(element.children[i]);
    }
}

function fixImageHeights(element) {
    all_images = Array.from(element.getElementsByTagName("img"));
    all_images.forEach((image) => {
        image.style.maxHeight = image.parentElement.offsetHeight + "px";
    });
    captioned = Array.from(element.getElementsByClassName("captioned"));
    captioned.forEach((captioned_image) => {
        let image = captioned_image.getElementsByTagName("img")[0];
        let caption = captioned_image.getElementsByClassName("caption")[0];
        image.style.maxHeight = image.parentElement.offsetHeight - caption.offsetHeight + "px";
    });
}

function fixFSHeights(element) {
    fixHeights(element);
    fixImageHeights(element);
}
