import 'preact/debug';
import { html } from 'htm/preact';
import { render } from 'preact';
import { useState } from 'preact/hooks';

const FermentingItem = (props) => {

  const toggleOp = (op) => {
    props.setOp(op);
    props.formToggle(!props.formVisible);
  };

  return html`
    <div>
      <div class="mb-2">
        <span class="has-text-weight-bold">${props.data.name}</span>
        <span class="ml-2">
          <button class="button is-small is-primary is-light mr-2" onClick=${() => toggleOp('transfer')}>przelej</button>
          <button class="button is-small is-primary is-light mr-2" onClick=${() => toggleOp('package')}>rozlej</button>
          <a class="button is-small is-primary is-light" href="${props.data.url}">edycja</a>
        </span>
      </div>
    </div>
  `;
}

const ActionForm = (props) => {
  let formClass = '';
  if (!props.visible) {
    formClass = 'is-hidden';
  }
  return html`
    <div class=${formClass}>
      <form onSubmit=${props.onSubmit}>
        <input class="input" type="number" name="fg" step="0.1" onInput=${props.setFg} />
        <input class="input" type="date" name="date" onInput=${props.setDate} />
        <textarea class="textarea" name="notes" onInput=${props.setNotes}></textarea>
        <button type="submit" class="button is-primary">wyślij</button>
      </form>
    </div>
  `;  
}

const Fermenting = ({ brews, csrfToken }) => {
  const [fg, setFg] = useState('');
  const [date, setDate] = useState(new Date())
  const [notes, setNotes] = useState('');
  const [formVisible, setFormVisible] = useState(false);
  const [op, setOp] = useState('');

  const onSubmit = (event) => {
    event.preventDefault();
    const url = `/brew/api/${op}`;
    fetch(url, {
      method: 'POST',
      headers: {
        'X-CSRFToken': csrfToken,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ fg, date, notes })
    })
      .then((resp) => {
        if (!resp.ok) {
          throw new Error(`Response: ${resp.status}`);
        }
        resp.json();
      })
      .then((data) => console.log(data))
      .catch((err) => console.error('HTTP fetch error:', err));
  };

  return html`
    <div class="column">
      <div class="box">
        <h2>Fermentuje</h2>
        ${brews.map((brew) => html`
          <${FermentingItem}
            data=${brew}
            key=${brew.id}
            formToggle=${setFormVisible}
            formVisible=${formVisible}
            setOp=${setOp}
          />
        `)}
        <${ActionForm}
          setFg=${setFg}
          setDate=${setDate}
          setNotes=${setNotes}
          onSubmit=${onSubmit}
          visible=${formVisible}
        />
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

const Dashboard = ({ brewsets, csrfToken }) => {
  return html`
    <div>
      <div class="columns">
        <${Fermenting} brews=${brewsets.fermenting} token=${csrfToken} />
        <${Maturing} brews=${brewsets.maturing} />
      </div>
      <div class="columns">
        <${Dispensing} brews=${brewsets.dispensing} />
        <${Recipes} brews=${brewsets.recipes} />
      </div>
    </div>
  `;
}

export { Dashboard, render, html }
