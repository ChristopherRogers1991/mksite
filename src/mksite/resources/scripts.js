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
