import { waitForElement } from "./waitForElement.js";

export async function listenForIFrameLoaded(selector, onLoaded) {
    const iFrame = await waitForElement(selector);
    if (iFrame) {
        iFrame.onload = () => {
            if (onLoaded) {
                onLoaded();
            }
        };
    } else {
        console.warn(
            `Unable to find element with ${selector} selector.`);
    }
}

export function scrollIntoView(id) {
    const element = document.getElementById(id);
    if (element) {
        element.scrollIntoView({
            behavior: 'smooth',
            block: 'end',
            inline: 'nearest'
        });
    }
}