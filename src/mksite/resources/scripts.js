function fullScreenImage(image) {
      if (document.fullscreenElement != null && document.fullscreenElement !== image) {
          return;
      }
      else if (document.fullscreenElement === image) {
        if (document.exitFullscreen) {
          document.exitFullscreen();
        }
        else {
          document.webkitCancelFullScreen();
        }
      }
      else {
        if (image.requestFullscreen) {
          image.requestFullscreen();
        }
        else {
          image.webkitRequestFullScreen();
        }
      }
};

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
    clearContainer();
    container.requestFullscreen();
    container.innerHTML = rows[container.displaying].outerHTML;
    viewingSlides = true;
}

function nextSlide() {
    if (container.displaying < rows.length - 1) {
        container.displaying += 1;
        container.innerHTML = rows[container.displaying].outerHTML;
    }
}

function previousSlide() {
    if (container.displaying > 0) {
        container.displaying -= 1;
        container.innerHTML = rows[container.displaying].outerHTML;
    }
}

document.addEventListener('fullscreenchange', (event) => {
    if (!document.fullscreenElement) {
        clearContainer();
        viewingSlides = false;
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