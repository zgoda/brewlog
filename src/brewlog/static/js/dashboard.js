import 'preact/debug';
import { h, render } from 'preact';
import { useState } from 'preact/hooks';

const FermentingItem = (props) => {

  const toggleOp = (op) => {
    props.setOp(op);
    const nextState = !props.formVisible;
    props.formToggle(nextState);
    if (nextState) {
      props.setCurItem(props.data.id);
    } else {
      props.setCurItem(0);
    }
  };

  return (
    <div>
      <div class="mb-2">
        <span class="has-text-weight-bold">{props.data.name}</span>
        <span class="ml-2">
          <button class="button is-small is-primary is-light mr-2" onClick={() => toggleOp('transfer')}>przelej</button>
          <button class="button is-small is-primary is-light mr-2" onClick={() => toggleOp('package')}>rozlej</button>
          <a class="button is-small is-primary is-light" href="{props.data.url}">edycja</a>
        </span>
      </div>
    </div>
  )
}

const ActionForm = (props) => {
  const opLabels = {
    transfer: 'przelej',
    package: 'rozlej'
  };
  let formClass = '';
  if (!props.visible) {
    formClass = 'is-hidden';
  }

  return (
    <div class={formClass}>
      <p class="has-text-weight-bold">{opLabels[props.op]}</p>
      <form onSubmit={props.onSubmit}>
        <div class="field">
          <label class="label">Gęstość</label>
          <div class="control">
            <input class="input" type="number" name="fg" step="0.1" onInput={props.setFg} value={props.fg} />
          </div>
        </div>
        <div class="field">
          <label class="label">Data</label>
          <div class="control">
            <input class="input" type="date" name="date" onInput={props.setDate} value={props.date} />
          </div>
        </div>
        <div class="field">
          <label class="label">Notatki</label>
          <div class="control">
            <textarea class="textarea" name="notes" onInput={props.setNotes}>{props.notes}</textarea>
          </div>
        </div>
        <div class="field">
          <div class="control">
            <button type="submit" class="button is-primary">wyślij</button>
          </div>
        </div>
      </form>
    </div>
  )
}

const Fermenting = ({ brews, csrfToken }) => {
  const [fg, setFg] = useState('');
  const [date, setDate] = useState('');
  const [notes, setNotes] = useState('');
  const [formVisible, setFormVisible] = useState(false);
  const [op, setOp] = useState('');
  const [curItem, setCurItem] = useState(0);

  const changeFg = (event) => {
    setFg(event.target.value);
  }

  const changeDate = (event) => {
    setDate(event.target.value);
  }

  const changeNotes = (event) => {
    setNotes(event.target.value);
  }

  const onSubmit = (event) => {
    event.preventDefault();
    const url = `/brew/api/${op}`;
    fetch(url, {
      method: 'POST',
      headers: {
        'X-CSRFToken': csrfToken,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ fg, date, notes, pk: curItem })
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

  return (
    <div class="column">
      <div class="box">
        <h2>Fermentuje</h2>
        {brews.map((brew) => (
          <FermentingItem
            data={brew}
            key={brew.id}
            formToggle={setFormVisible}
            setCurItem={setCurItem}
            formVisible={formVisible}
            setOp={setOp}
          />
        ))}
        <ActionForm
          fg={fg}
          setFg={changeFg}
          date={date}
          setDate={changeDate}
          notes={notes}
          setNotes={changeNotes}
          onSubmit={onSubmit}
          visible={formVisible}
          op={op}
        />
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
