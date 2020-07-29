import { html } from 'htm/preact';

const FermentingItem = ({ data }) => {
  return html`
    <div>
      <div class="mb-2 has-text-weight-bold">${data.name}</div>
      <div class="buttons are-small">
        <button class="button is-primary is-light">przelej</button>
        <button class="button is-primary is-light">rozlej</button>
        <button class="button is-primary is-light">pomiar</button>
      </div>
    </div>
  `;
}

const Fermenting = ({ brews }) => {
  return html`
    <div class="column">
      <div class="box">
        <h2>Fermentuje</h2>
        ${brews.map((brew) => html`
          <${FermentingItem} data=${brew} key=${brew.id} />
        `)}
      </div>
    </div>
  `;
}

const Maturing = ({ brews }) => {
  return html`
    <div class="column">
      <div class="box">
        <h2>Dojrzewa</h2>
        <div>
          <p>${brews.length}</p>
        </div>
      </div>
    </div>
  `;
}

const Dispensing = ({ brews }) => {
  return html`
    <div class="column">
      <div class="box">
        <h2>Wyszynk</h2>
        <div>
          <p>${brews.length}</p>
        </div>
      </div>
    </div>
  `;
}

const Recipes = ({ brews }) => {
  return html`
    <div class="column">
      <div class="box">
        <h2>Receptury</h2>
        <div>
          <p>${brews.length}</p>
        </div>
      </div>
    </div>
  `;
}

export const Dashboard = ({ brewsets }) => {
  return html`
    <div>
      <div class="columns">
        <${Fermenting} brews=${brewsets.fermenting} />
        <${Maturing} brews=${brewsets.maturing} />
      </div>
      <div class="columns">
        <${Dispensing} brews=${brewsets.dispensing} />
        <${Recipes} brews=${brewsets.recipes} />
      </div>
    </div>
  `;
}
