import 'preact/debug';
import { h, render } from 'preact';
import { useState } from 'preact/hooks';

const FermentingItem = (props) => {
  const [showModal, setModal] = useState(false);
  const [op, setOp] = useState('');

  const onClose = () => setModal(false);

  const toggleOp = (op) => {
    setOp(op);
    setModal(true);
  };

  return (
    <div>
      <div class="mb-2">
        <span class="has-text-weight-bold">{props.data.name}</span>
        <span class="ml-2">
          <button class="button is-small is-primary is-light mr-2" onClick={() => toggleOp('transfer')}>przelej</button>
          <button class="button is-small is-primary is-light mr-2" onClick={() => toggleOp('package')}>rozlej</button>
          <a class="button is-small is-primary is-light" href={props.data.url}>edycja</a>
        </span>
      </div>
      {showModal && (
        <ActionForm
          setModal={setModal}
          showModal={showModal}
          onClose={onClose}
          op={op}
          csrfToken={props.token}
          brew={props.data}
        />
      )}
    </div>
  )
}

const ActionForm = (props) => {
  const [fg, setFg] = useState(0);
  const [date, setDate] = useState('');
  const [notes, setNotes] = useState('');

  const opLabels = {
    transfer: `Przelej ${props.brew.name}`,
    package: `Rozlew ${props.brew.name}`
  };

  let modalClass = 'modal';
  if (props.showModal) {
    modalClass = 'modal is-active';
  }

  const onSubmit = (event) => {
    event.preventDefault();
    const url = `/brew/api/${props.op}`;
    fetch(url, {
      method: 'POST',
      headers: {
        'X-CSRFToken': props.csrfToken,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ fg, date, notes, pk: props.brew.id })
    })
      .then((resp) => {
        if (!resp.ok) {
          throw new Error(`Response: ${resp.status}`);
        }
        resp.json();
        props.onClose();
      })
      .then((data) => console.log(data))
      .catch((err) => console.error('HTTP fetch error:', err));
  };

  return (
    <div class={modalClass}>
      <div class="modal-background" />
      <div class="modal-content">
        <div class="box">
          <p class="has-text-weight-bold">{opLabels[props.op]}</p>
          <form onSubmit={onSubmit}>
            <div class="field">
              <label class="label">Gęstość</label>
              <div class="control">
                <input class="input" type="number" name="fg" step="0.1" onInput={setFg} value={fg} />
              </div>
            </div>
            <div class="field">
              <label class="label">Data</label>
              <div class="control">
                <input class="input" type="date" name="date" onInput={setDate} value={date} />
              </div>
            </div>
            <div class="field">
              <label class="label">Notatki</label>
              <div class="control">
                <textarea class="textarea" name="notes" onInput={setNotes}>{notes}</textarea>
              </div>
            </div>
            <div class="field">
              <div class="control">
                <button type="submit" class="button is-primary">wyślij</button>
              </div>
            </div>
          </form>
        </div>
      </div>
      <button class="modal-close is-large" aria-label="close" onClick={() => props.onClose()} />
    </div>
  )
}

const Fermenting = ({ brews, csrfToken }) => {
  return (
    <div class="column">
      <div class="box">
        <h2>Fermentuje</h2>
        {brews.map((brew) => (
          <FermentingItem
            data={brew}
            key={brew.id}
            token={csrfToken}
          />
        ))}
      </div>
    </div>
  );
}

const Maturing = ({ brews }) => {
  return (
    <div class="column">
      <div class="box">
        <h2>Dojrzewa</h2>
        <div>
          <p>{brews.length}</p>
        </div>
      </div>
    </div>
  );
}

const Dispensing = ({ brews }) => {
  return (
    <div class="column">
      <div class="box">
        <h2>Wyszynk</h2>
        <div>
          <p>{brews.length}</p>
        </div>
      </div>
    </div>
  );
}

const Recipes = ({ brews }) => {
  return (
    <div class="column">
      <div class="box">
        <h2>Receptury</h2>
        <div>
          <p>{brews.length}</p>
        </div>
      </div>
    </div>
  );
}

const Dashboard = ({ brewsets, csrfToken }) => {
  return (
    <div>
      <div class="columns">
        <Fermenting brews={brewsets.fermenting} token={csrfToken} />
        <Maturing brews={brewsets.maturing} />
      </div>
      <div class="columns">
        <Dispensing brews={brewsets.dispensing} />
        <Recipes brews={brewsets.recipes} />
      </div>
    </div>
  );
}

export { Dashboard, render, h };
