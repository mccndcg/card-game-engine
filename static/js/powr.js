const x = Vue.createApp({
  delimiters : ['[[', ']]'],
  data () {
    return {
      cards: 0
    }
  }
})

const axios_instance = axios.create({
  baseURL: 'http://127.0.0.1:5000/',
  timeout: 1000,
  headers: {
    'X-Custom-Header': 'foobar',
    }
});




x.component('addState',{
    template: `
      <button :class="state" @click=addStateClick(state)>add</button>`,
    props: ['state'],
    methods: {
      addStateClick(state) {
        if('condition'==='a') {console.log('NICE')}
      }
    }
    })


x.component('state-display', {
  emits: ['fetchedData'],
  data() {
    return {
      states: {}
    }
  },
  created () {
    axios_instance.post('/get_states',
              {'a':'a'}
            )
      .then(response => {
        this.states = response.data
      })
      .catch(function (error) {
        console.log(error);
      })
    },
  template: `
    <div>
      <p v-for="(substate, state) in states">
        <addState :state="state"></addState> {{state}}
        <div style="margin: 20px">
        <p v-for="(property, substate) in substate">
          <button>add</button>... {{substate}}
          <div style="margin: 20px">
            <p v-if="typeof property === 'string'">........{{property}}</p>
            <template v-else>
            <p v-for="(index, property) in property">
            <button>edt</button><button>del</button>{{index}}</p></template>
          </div>
        </p>
        </div>
      </p>
    </div>`,
  methods: {
    async fetchCards() {
      axios_instance.post('/get_cards',
              [{'a':'a'}]
            )
      .then(response => {
        this.states = response.data
      })
      .catch(function (error) {
        console.log(error);
      })
    }
  }
})
