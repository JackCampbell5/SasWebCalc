import 'https://cdnjs.cloudflare.com/ajax/libs/plotly.js/2.17.1/plotly.min.js';

const template = `
<div class="instrument_params">
  <h3>{{title}}</h3>
</div>
`

export default {
  props: {
    title: String
  },
  data: () => ({
    params: {

    }
  }),
  template: template
}