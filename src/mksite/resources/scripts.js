let scrollXPosition = 0;
let scrollYPosition = 0;

window.addEventListener('load', () => {
  const loader = document.getElementById('loader');
  loader.style.display = 'none';
});

function toggleFullscreen(element) {
    if (browserIsFullscreen() && element === getFullscreenElement()) {
        exitFullscreen();
    }
    else {
        enterFullscreen(element);
    }
}

async function enterFullscreen(element) {
    if (browserIsFullscreen()) {
        return;
    }
    scrollXPosition = window.scrollX;
    scrollYPosition = window.scrollY;
    if (element.requestFullscreen) {
        await element.requestFullscreen({ navigationUI: "hide" });
    }
    else if (element.mozRequestFullScreen) {
        await element.mozRequestFullScreen({ navigationUI: "hide" });
    }
    else if (element.webkitRequestFullScreen) {
        await element.webkitRequestFullScreen();
    }
    else if (element.msRequestFullscreen) {
        await element.msRequestFullscreen();
    }
}

async function exitFullscreen(){
    const exit = document.exitFullscreen
         || document.mozCancelFullScreen
         || document.webkitCancelFullScreen
         || document.msExitFullscreen;

    if (exit) {
        await exit.call(document);
        // Wait for the browser to complete its layout reflow and fullscreen transition
        await new Promise(resolve => requestAnimationFrame(() => requestAnimationFrame(resolve)));
        await window.scrollTo(scrollXPosition, scrollYPosition);
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
let rowsContainer;
let fullscreenContainer;
let helpButton = document.getElementById("help");
let helpDialog = document.getElementById("help-dialog");
let slideshowButton = document.getElementById("slideshow-button");
let viewingSlides = false;

document.addEventListener("DOMContentLoaded", (event) => {
    rows = document.getElementsByClassName("row");
    rowsContainer = document.getElementById("rows-container");
    fullscreenContainer = document.getElementById("fullscreen-container");
    helpButton = document.getElementById("help");
    helpDialog = document.getElementById("help-dialog");
    slideshowButton = document.getElementById("slideshow-button");
    document.onmousemove = function() {
        document.body.style.cursor = "default";
        if (viewingSlides) {
            window.setTimeout(function() {document.body.style.cursor = "none"}, 1000)
        }
    };
    initAspectRatios();
    calculateRowLayouts();
});

window.addEventListener("resize", calculateRowLayouts);

/**
 * Copy data-aspect-ratio attributes to CSS custom properties so that
 * CSS can use aspect-ratio: var(--aspect-ratio) without inline styles.
 */
function initAspectRatios() {
    document.querySelectorAll('.zoomable[data-aspect-ratio]').forEach((el) => {
        el.style.setProperty('--aspect-ratio', el.dataset.aspectRatio);
    });
}

/**
 * For multi-image rows, set flex-grow proportional to each image's aspect ratio
 * so that all images share the same height while maintaining their original
 * aspect ratios. A wider image (larger W/H ratio) gets a larger flex-grow,
 * making it wider but keeping the height equal across the row.
 */
function calculateRowLayouts() {
    const multiImageRows = document.querySelectorAll(".image-image.row, .image-image-image.row");

    multiImageRows.forEach((row) => {
        const zoomables = row.querySelectorAll(".zoomable[data-aspect-ratio]");
        if (zoomables.length < 2) return;

        const ratios = Array.from(zoomables).map((z) => {
            const parts = z.dataset.aspectRatio.split("/");
            return parts[0] / parts[1];
        });

        zoomables.forEach((z, i) => {
            z.style.flexGrow = ratios[i];
            z.style.flexShrink = 0;
            z.style.flexBasis = "0";
        });
    });
}

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

async function slideShow() {
    if (fullscreenContainer.displaying == undefined) {
        fullscreenContainer.displaying = 0;
    }
    await enterFullscreen(fullscreenContainer);
    fullscreenContainer.innerHTML = rows[fullscreenContainer.displaying].outerHTML;
    fixFSHeights(fullscreenContainer)
    viewingSlides = true;
}

const sleep = ms => new Promise(r => setTimeout(r, ms));

const isHttp = ["http:", "https:"].includes(location.protocol);

async function nextSlide() {
    if (isHttp && rows[fullscreenContainer.displaying + 1].classList.contains("footer")) {
        const nextRows = await getNextPageOfRows(document.getElementById("next-url").href);
        rowsContainer.removeChild(document.getElementById("footer"));
        const length = nextRows.length;
        for (let i = 0; i < length; i++) {
            /* This language is terrible. Appending nextRows[i] consumes the value from
               nextRows for some reason, meaning we have to save the length as a constant
               for the loop, and always append the 0th element. Note that it is only consumed
               when it is appended. If you just iterate over the items and access them, e.g.
               to log them, count them, etc, that works as expected. As soon as they are
               appended to the rowsContainer, they are consumed. This means other loop styles,
               e.g. `for (let item of nextRows)` also do not work, if appending the items. */
            rowsContainer.append(nextRows[0]);
        }
    }
    if (fullscreenContainer.displaying < rows.length - 1) {
        fullscreenContainer.style.opacity = 0;
        await sleep(500);
        fullscreenContainer.displaying += 1;
        fullscreenContainer.innerHTML = rows[fullscreenContainer.displaying].outerHTML;
        fixFSHeights(fullscreenContainer)
        fullscreenContainer.style.opacity = 1;
    }
}


async function previousSlide() {
    if (fullscreenContainer.displaying > 0) {
        fullscreenContainer.style.opacity = 0;
        await sleep(500);
        fullscreenContainer.displaying -= 1;
        fullscreenContainer.innerHTML = rows[fullscreenContainer.displaying].outerHTML;
        fixFSHeights(fullscreenContainer)
        fullscreenContainer.style.opacity = 1;
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
   fullscreenContainer.innerHTML = '';
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

function fixHeights(element, height) {
    if (element.children.length == 0) {
        return;
    }
    element.style.maxHeight = height;
    for (let i = 0; i < element.children.length; i++) {
        fixHeights(element.children[i], height);
    }
}

/* Set the maxHeight of leaf elements (img, iframe, video) so they fit
   within the fullscreen container while preserving aspect ratio. */
function fixTagHeights(element, tag, height) {
    const all_tag = Array.from(element.getElementsByTagName(tag));
    all_tag.forEach((tag_element) => {
        tag_element.style.maxHeight = height + "px";
    });
    const captioned = Array.from(element.getElementsByClassName("captioned"));
    captioned.forEach((captioned_tag) => {
        let tag_element = captioned_tag.getElementsByTagName(tag)[0];
        if (tag_element == undefined) {
            return;
        }
        let caption = captioned_tag.getElementsByClassName("caption")[0];
        tag_element.style.maxHeight = (height - caption.offsetHeight) + "px";
    });
}

/* This is a hack, to get around different browsers handling CSS
   in different ways - it was possible to get the desired effect (elements
   as large as possible, without pushing captions offscreen) in
   Chrome/Firefox, but not webkit, OR webkit, but not Chrome/Firefox. */
function fixFSHeights(element, flag = true) {
    const height = fullscreenContainer.offsetHeight;
    fixHeights(element, height);
    fixTagHeights(element, "img", height);
    fixTagHeights(element, "iframe", height);
    fixTagHeights(element, "video", height);
}


async function getNextPageOfRows(url) {
    const page = await fetch(url)
    const parser = new DOMParser()
    const doc = parser.parseFromString(await page.text(), 'text/html');
    return doc.getElementsByClassName("row");
}
