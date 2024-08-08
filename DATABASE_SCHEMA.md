# Database Schema Documentation

## Collections

### Rounds

| Field             | Type     | Description                                                      |
|-------------------|----------|------------------------------------------------------------------|
| `_id`             | ObjectId | Unique identifier for the round.                                 |
| `series`          | String   | Tournament name. Examples: `Longhorn`, `Area F`, `NJCL`, etc.    |
| `division`        | String   | Difficulty level of the packet. Possible values: `novice`, `intermediate`, `advanced`, `elite`. |
| `year`            | Int32    | The year the packet was created.                                 |
| `number`          | String   | Either a number, or the word `finals`.                           |
| `tier`            | String   | Possible values: `local`, `regional`, `state`, `national`.       |
| `source_url`      | String   | URL source of the packet.                                        |

### Questions

| Field                  | Type   | Description                             |
|------------------------|--------|-----------------------------------------|
| `_id`                  | String | Unique identifier for the question.     |
| `packet_id`            | String | Identifier of the associated packet.    |
| `round_id`             | String | Identifier of the associated round.     |
| `number`               | Number | Number of the question in the round.    |
| `category`             | String | Possible values: `language`, `history`, `mythology`, `life`, `literature`.|
| `division`             | String | Duplicated from `packets`.               |
| `question`             | String | The text of the question.               |
| `answer`               | String | Answer to the question.                 |
| `bonuses`              | Array  | Array of bonus objects related to the question. Each bonus object contains:
|                        |        | - `question`: A related question for the bonus.            |
|                        |        | - `answer`: The answer associated with the bonus question. |
