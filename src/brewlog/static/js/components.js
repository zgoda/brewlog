import { html } from 'htm/preact';

const Icon = (name) => {
  return html`<svg><use xlink:href="#${name}"></svg>`;
};

export { Icon };
