import {evaluate} from '../site/model-utils.js';
let text='';for await (const chunk of process.stdin)text+=chunk;process.stdout.write(JSON.stringify(JSON.parse(text).map(c=>evaluate(c.events,c.observed,c.as_of))));
