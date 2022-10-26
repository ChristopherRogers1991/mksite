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
let viewingSlides = false;

document.addEventListener("DOMContentLoaded", (event) => {
    rows = document.getElementsByClassName("row");
    container = document.getElementById("fullscreen-container");
});

function slideShow() {
    document.addEventListener("keydown", (event) => {
        if (document.fullscreenElement !== container) {
            return;
        }
        if (event.key == "ArrowRight") {
            nextSlide();
        }
        if (event.key == "ArrowLeft") {
            previousSlide();
        }
    });
    container.displaying = 0;
    clearContainer();
    container.requestFullscreen();
    container.innerHTML = rows[container.displaying].outerHTML;
    viewingSlides = true;
}

function nextSlide() {
    if (container.disaplaying != rows.length - 1) {
        container.displaying += 1;
        container.innerHTML = rows[container.displaying].outerHTML;
    }
}

function previousSlide() {
    if (container.displaying != 0) {
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
    const button = document.getElementById("help");
    const dialog = document.getElementById("help-dialog");
    if (viewingSlides) {
        if (event.clientX >= window.innerWidth / 2) {
            nextSlide();
        } else {
            previousSlide()
        }
        return;
    }
    else if (event.target != button) {
        dialog.style.display = "none";
    }
}