function fullScreenImage(image) {
      if (document.fullscreenElement != null || document.webkitFullscreenElement != null) {
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

window.onload = (event) => {
    rows = document.getElementsByClassName("row");
    container = document.getElementById("fullscreen-container");
};

function slideShow() {
    document.addEventListener("keydown", (event) => {
        if (document.fullscreenElement !== container) {
            return;
        }
        if (event.key == "ArrowRight" && container.displaying != rows.length - 1) {
            container.displaying += 1;
        }
        if (event.key == "ArrowLeft" && container.displaying != 0) {
            container.displaying -= 1;
        }
        container.innerHTML = rows[container.displaying].outerHTML;
    });
    container.displaying = 0;
    clearContainer();
    container.requestFullscreen();
    container.innerHTML = rows[container.displaying].outerHTML;
}

document.addEventListener('fullscreenchange', (event) => {
    if (!document.fullscreenElement) {
        clearContainer();
    }
});

function clearContainer() {
   container.innerHTML = '';
}
