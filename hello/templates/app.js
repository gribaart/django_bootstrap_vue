export default {
    name: 'Test',

    setup() {
        const title = "Hello";

        return {
            title
        };
    },

    template: `
      <div>
        <h1>{{title}}</h1>
      </div>
    `,
};