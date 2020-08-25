import 'preact/debug';
import { h, render } from 'preact';
import { useState } from 'preact/hooks';
import {
  CarbonationSelect, CarbonationTypeSelect, DateInput, ModalForm,
  NumberInput, TextArea,
} from './components/forms';

const FermentingItem = (({ data, csrfToken, brewsChanged }) => {
  const [showModal, setModal] = useState(false);
  const [op, setOp] = useState('');

  const onClose = () => {
    setModal(false);
    setOp('');
  };

  const toggleOp = (op) => {
    setOp(op);
    setModal(true);
  };

  return (
    <div>
      <div class="mb-2">
        <span class="has-text-weight-bold">{data.name}</span>
        <span class="ml-2">
          <button class="button is-small is-primary is-light mr-2" onClick={() => toggleOp('transfer')}>przelej</button>
          <button class="button is-small is-primary is-light mr-2" onClick={() => toggleOp('package')}>rozlej</button>
          <a class="button is-small is-primary is-light" href={data.url}>edycja</a>
        </span>
      </div>
      {showModal && (
        <FermentingActionForm
          setModal={setModal}
          showModal={showModal}
          onClose={onClose}
          op={op}
          csrfToken={csrfToken}
          brew={data}
          brewsChanged={brewsChanged}
        />
      )}
    </div>
  )
});

const MaturingItem = (({ data }) => {
  return (
    <div class="mb-2">
      <span class="has-text-weight-bold">{data.name}</span>
    </div>
  )
});

const DispensingItem = (({ data }) => {
  return (
    <div class="mb-2">
      <span class="has-text-weight-bold">{data.name}</span>
    </div>
  )
});

const RecipeItem = (({ data }) => {
  return (
    <div class="mb-2">
      <span class="has-text-weight-bold">{data.name}</span>
      <span class="ml-2">
        <a class="button is-small is-primary is-light" href={data.url}>edycja</a>
      </span>
    </div>
  )
});

const FermentingActionForm = (props) => {
  const [fg, setFg] = useState(0);
  const [volume, setVolume] = useState(0);
  const [date, setDate] = useState('');
  const [notes, setNotes] = useState('');
  const [carbonation, setCarbonation] = useState('');
  const [carbType, setCarbType] = useState('');

  const opLabels = {
    transfer: `Przelej ${props.brew.name}`,
    package: `Rozlew ${props.brew.name}`
  };

  const onSubmit = (async (event) => {
    event.preventDefault();
    const url = `/brew/api/${props.op}`;
    const resp = await fetch(url, {
      method: 'POST',
      headers: {
        'X-CSRFToken': props.csrfToken,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(
        { volume, fg, date, carbonation, carbtype: carbType, notes, id: props.brew.id }
      ),
      credentials: 'same-origin'
    });
    if (resp.ok) {
      const data = await resp.json();
      console.log(data);
      if (props.op === 'package') {
        props.brewsChanged(['fermenting', 'maturing']);
      }
    } else {
      console.log(`HTTP fetch error: ${resp.status}`);
    }
    props.onClose();
  });

  const changeFg = ((e) => {
    setFg(e.target.value);
  });

  const changeDate = ((e) => {
    setDate(e.target.value);
  });

  const changeNotes = ((e) => {
    setNotes(e.target.value);
  })

  const changeVolume = ((e) => {
    setVolume(e.target.value);
  });

  let fields = [
    <NumberInput label='Objętość' name='volume' step='0.1' setValue={changeVolume} value={volume} />,
    <NumberInput label='Gęstość' name='fg' step='0.1' setValue={changeFg} value={fg} />,
    <DateInput label='Data' name='date' setValue={changeDate} value={date} />,
  ];
  if (props.op === 'package') {
    fields.push(
      <CarbonationTypeSelect carbType={carbType} setCarbType={setCarbType} />,
      <CarbonationSelect carbonation={carbonation} setCarbonation={setCarbonation} />
    );
  }
  fields.push(
    <TextArea label='Notatki' name='notes' setValue={changeNotes} value={notes} />
  );

  return (
    <ModalForm
      closeHandler={props.onClose}
      label={opLabels[props.op]}
      active={props.showModal}
      fields={fields}
      submitHandler={onSubmit}
    />
  )
}

const Fermenting = ({ brews, csrfToken, brewsChanged }) => {
  return (
    <div class="column">
      <div class="box">
        <h2>Fermentuje</h2>
        {brews.map((brew) => (
          <FermentingItem
            data={brew}
            key={brew.id}
            csrfToken={csrfToken}
            brewsChanged={brewsChanged}
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
        {brews.map((brew) => (
          <MaturingItem data={brew} key={brew.id} />
        ))}
      </div>
    </div>
  );
}

const Dispensing = ({ brews }) => {
  return (
    <div class="column">
      <div class="box">
        <h2>Wyszynk</h2>
        {brews.map((brew) => (
          <DispensingItem data={brew} key={brew.id} />
        ))}
      </div>
    </div>
  );
}

const Recipes = ({ brews }) => {
  return (
    <div class="column">
      <div class="box">
        <h2>Receptury</h2>
        {brews.map((brew) => (
          <RecipeItem data={brew} key={brew.id} />
        ))}
      </div>
    </div>
  );
}

const Dashboard = ({ brewsets, csrfToken }) => {
  const [fermenting, setFermenting] = useState(brewsets.fermenting);
  const [maturing, setMaturing] = useState(brewsets.maturing);
  const [dispensing, setDispensing] = useState(brewsets.dispensing);
  const [recipes, setRecipes] = useState(brewsets.recipes);

  const updateBrewState = ((data, brewTypes) => {
    brewTypes.map((name) => {
      switch (name) {
        case 'fermenting':
          setFermenting(data.fermenting);
          break;
        case 'maturing':
          setMaturing(data.maturing);
          break;
        case 'dispensing':
          setDispensing(data.dispensing);
          break;
        case 'recipes':
          setRecipes(data.recipes);
          break;
      }
    });
  });

  const brewsStateChanged = (async (changedTypes) => {
    let params = [];
    changedTypes.map((typeName) => {
      params.push(`state=${typeName}`);
    });
    const queryStr = params.join('&')
    const url = `/brew/api/brews?${queryStr}`;
    const resp = await fetch(url, {
      credentials: 'same-origin'
    })
    if (resp.ok) {
      const data = await resp.json();
      updateBrewState(data, changedTypes);
      console.log(data);        
    } else {
      console.error(`HTTP fetch error: ${resp.status}`);
    }
  });

  return (
    <div>
      <div class="columns">
        <Fermenting
          brews={fermenting} csrfToken={csrfToken} brewsChanged={brewsStateChanged}
        />
        <Maturing brews={maturing} />
      </div>
      <div class="columns">
        <Dispensing brews={dispensing} />
        <Recipes brews={recipes} />
      </div>
    </div>
  );
}

export { Dashboard, render, h };
