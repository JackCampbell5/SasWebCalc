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