import { html } from "./preact.min.js";

const Fermenting = ({ brews }) => {
  return html`
    <div class="column">
      <div class="panel is-info">
        <div class="panel-heading">Fermentuje</div>
        <div class="panel-block">
          <p>${brews.length}</p>
        </div>
      </div>
    </div>
  `;
}

const Maturing = ({ brews }) => {
  return html`
    <div class="column">
      <div class="panel is-info">
        <div class="panel-heading">Dojrzewa</div>
        <div class="panel-block">
          <p>${brews.length}</p>
        </div>
      </div>
    </div>
  `;
}

const Dispensing = ({ brews }) => {
  return html`
    <div class="column">
      <div class="panel is-info">
        <div class="panel-heading">Wyszynk</div>
        <div class="panel-block">
          <p>${brews.length}</p>
        </div>
      </div>
    </div>
  `;
}

const Recipes = ({ brews }) => {
  return html`
    <div class="column">
      <div class="panel is-info">
        <div class="panel-heading">Receptury</div>
        <div class="panel-block">
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
