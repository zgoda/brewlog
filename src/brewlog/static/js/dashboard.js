import 'preact/debug';
import { h, render, Fragment } from 'preact';
import { useState } from 'preact/hooks';
import {
  CarbonationSelect, CarbonationTypeSelect, DateInput, ModalForm,
  NumberInput, TextArea, ActionLinkButton, ActionButton, TextInput,
} from './components/forms';

const PanelTitle = (({ label }) => {
  return <span class="has-text-weight-bold">{label}</span> 
});

const FermentingItem = (({ data, csrfToken, brewsChanged }) => {
  const [showModal, setModal] = useState(false);
  const [op, setOp] = useState('');

  const onClose = (() => {
    setModal(false);
    setOp('');
  });

  const toggleOp = ((op) => {
    setOp(op);
    setModal(true);
  });

  const setTransferOp = (() => {
    toggleOp('transfer');
  });

  const setPackageOp = (() => {
    toggleOp('package');
  });

  return (
    <Fragment>
      <div class="mb-2">
        <PanelTitle label={data.name} />
        <span class="ml-2">
          <ActionButton theresMore={true} clickHandler={setTransferOp} label='przelej' />
          <ActionButton theresMore={true} clickHandler={setPackageOp} label='rozlej' />
          <ActionLinkButton url={data.url} label='edycja' />
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
    </Fragment>
  )
});

const MaturingItem = (({ data }) => {
  return (
    <div class="mb-2">
      <PanelTitle label={data.name} />
    </div>
  )
});

const DispensingItem = (({ data }) => {
  return (
    <div class="mb-2">
      <PanelTitle label={data.name} />
    </div>
  )
});

const RecipeItem = (({ data }) => {
  return (
    <div class="mb-2">
      <PanelTitle label={data.name} />
      <span class="ml-2">
        <ActionLinkButton url={data.url} label='edycja' />
      </span>
    </div>
  )
});

const FermentingActionForm = (({ brew, op, csrfToken, brewsChanged, onClose, showModal }) => {
  const [fg, setFg] = useState(0);
  const [volume, setVolume] = useState(0);
  const [date, setDate] = useState('');
  const [notes, setNotes] = useState('');
  const [carbonation, setCarbonation] = useState('');
  const [carbType, setCarbType] = useState('');
  const [stepName, setStepName] = useState('');
  const [temperature, setTemperature] = useState(0);

  const opLabels = {
    transfer: `Przelej ${brew.name}`,
    package: `Rozlew ${brew.name}`
  };

  const onSubmit = (async (event) => {
    event.preventDefault();
    const url = `/brew/api/${op}`;
    const resp = await fetch(url, {
      method: 'POST',
      headers: {
        'X-CSRFToken': csrfToken,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(
        {
          volume, fg, date, carbonation, carbtype: carbType, notes, id: brew.id,
          temperature, name: stepName,
        }
      ),
      credentials: 'same-origin'
    });
    if (resp.ok) {
      if (op === 'package') {
        brewsChanged(['fermenting', 'maturing']);
      }
    } else {
      console.log(`HTTP fetch error: ${resp.status}`);
    }
    onClose();
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

  const changeStepName = ((e) => {
    setStepName(e.target.value);
  });

  const changeTemperature = ((e) => {
    setTemperature(e.target.value);
  });

  const fields = [
    <NumberInput label='Objętość' name='volume' step='0.1' setValue={changeVolume} value={volume} />,
    <NumberInput label='Gęstość' name='fg' step='0.1' setValue={changeFg} value={fg} />,
    <DateInput label='Data' name='date' setValue={changeDate} value={date} />,
  ];
  if (op === 'package') {
    fields.push(
      <CarbonationTypeSelect carbType={carbType} setCarbType={setCarbType} />,
      <CarbonationSelect carbonation={carbonation} setCarbonation={setCarbonation} />,
    );
  } else {
    fields.push(
      <TextInput label='Nazwa' name='name' setValue={changeStepName} value={stepName} />,
      <NumberInput label='Temperatura' name='temperature' setValue={changeTemperature} value={temperature} />,
    )
  }
  fields.push(
    <TextArea label='Notatki' name='notes' setValue={changeNotes} value={notes} />
  );

  return (
    <ModalForm
      closeHandler={onClose}
      label={opLabels[op]}
      active={showModal}
      fields={fields}
      submitHandler={onSubmit}
    />
  )
});

const Fermenting = (({ brews, csrfToken, brewsChanged }) => {
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
});

const Maturing = (({ brews }) => {
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
});

const Dispensing = (({ brews }) => {
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
});

const Recipes = (({ brews }) => {
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
});

const Dashboard = (({ brewsets, csrfToken }) => {
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
    const params = [];
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
    } else {
      console.error(`HTTP fetch error: ${resp.status}`);
    }
  });

  return (
    <Fragment>
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
    </Fragment>
  );
});

export { Dashboard, render, h };
