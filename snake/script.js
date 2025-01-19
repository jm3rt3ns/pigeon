const GAMESPEED = 0.1 // this is a percent of 1 second and defines how long it takes for the snack to travel between grid pieces of the board
const HEIGHT_OF_SEGMENT_X = 25;
const HEIGHT_OF_SEGMENT_Y = 25;
const SNAKE_COLOR = '#42f572';
const SNACK_COLOR = '#f54842';
BOARD_SIZE_X = 20;
BOARD_SIZE_Y = 20;
const Directions = Object.freeze({
    North:   Symbol("North"),
    South:  Symbol("South"),
    East:  Symbol("East"),
    West:  Symbol("West"),
});

function getRandomInt(max) {
    return Math.floor(Math.random() * max);
}

function getVelocity(playerDirection) {
    switch (playerDirection) {
        case Directions.North:
            return [0,-1];
        case Directions.South:
            return [0,1];
        case Directions.West:
            return [-1,0];
        case Directions.East:
            return [1,0];
        default:
            return [0,0];
    }
}

function drawSegment(x, y, delta, playerDirection, gameId) {

    const velocity = getVelocity(playerDirection);
    // const smoothedX = velocity[0] * delta;
    // const smoothedY = velocity[1] * delta;
    const segment = document.createElement("div");
    segment.style.backgroundColor = SNAKE_COLOR;
    segment.style.position = 'absolute';
    segment.style.top = `${(y) * HEIGHT_OF_SEGMENT_Y}px`;
    segment.style.left = `${(x) * HEIGHT_OF_SEGMENT_X}px`;
    segment.style.width = `${HEIGHT_OF_SEGMENT_X}px`;
    segment.style.height = `${HEIGHT_OF_SEGMENT_Y}px`;
    segment.className = 'snake-segment';
    const gameObject = document.getElementById(gameId);
    gameObject.appendChild(segment);
    return segment;
}

function drawSnack(x, y, gameId) {
    const segment = document.createElement("div");
    segment.style.backgroundColor = SNACK_COLOR;
    segment.style.position = 'absolute';
    segment.style.top = `${y * HEIGHT_OF_SEGMENT_Y}px`;
    segment.style.left = `${x * HEIGHT_OF_SEGMENT_X}px`;
    segment.style.width = `${HEIGHT_OF_SEGMENT_X}px`;
    segment.style.height = `${HEIGHT_OF_SEGMENT_Y}px`;
    segment.id = 'snack';
    const gameObject = document.getElementById(gameId);
    gameObject.appendChild(segment);
    return segment;
}

function uuidv4() {
    return "10000000-1000-4000-8000-100000000000".replace(/[018]/g, c =>
      (+c ^ crypto.getRandomValues(new Uint8Array(1))[0] & 15 >> +c / 4).toString(16)
    );
  }


class Game {
    id = uuidv4();
    snakeArray = [];
    playerDirection = Directions.North;
    gameStartTime = null;

    snack = null;
    tick = 0;

    constructor() {
        this.handleKeypress = this.handleKeypress.bind(this);
        document.addEventListener('keyup', this.handleKeypress);

        const animate = () => {
            requestAnimationFrame((t) => animate(t));
            this.cycle(0);
        }
        requestAnimationFrame(animate);

    }

    destroy() {
        document.removeEventListener('keyup');
    }

    // handle direction change
    handleKeypress(event) {
        switch (event.code) {
            case 'ArrowDown':
                this.playerDirection = Directions.South;
                break;
            case 'ArrowLeft':
                this.playerDirection = Directions.West;
                break;
            case 'ArrowRight':
                this.playerDirection = Directions.East;
                break;
            case 'ArrowUp':
                this.playerDirection = Directions.North;
                break;
            default:
                console.debug('not a code we are interested in: ', event.code);
        }
    }

    resetGame() {
        this.snakeArray = [];
        this.playerDirection = Directions.North;
        this.gameStartTime = null;
        this.snack = null;
        this.tick = 0;
    }

    // t is a percent between steps that allows us to create smooth movement as the snake travels between positions
    cycle(t) {
        if (this.snakeArray.length === 0) {
            // we are beginning the game - position the snake somewhere
            this.snakeArray.push({ x: getRandomInt(BOARD_SIZE_X), y: getRandomInt(BOARD_SIZE_Y) });
            this.gameStartTime = Date.now();
        }

        if (this.snack === null) {
            this.snack = { x: getRandomInt(BOARD_SIZE_X), y: getRandomInt(BOARD_SIZE_Y) };
        }

        // more logic to follow here

        // check if enough time has elapsed to advance the game tick
        // this will be floor((current time - start time) / gamespeed). If this is greater than the current tick, then we advance the tick as well as move the snake, check for collisions, etc.
        const gameTime = (Date.now() - this.gameStartTime) / 1000 / GAMESPEED;
        let delta = 0;
        if (Math.floor(gameTime) > this.tick) {
            const velocity = getVelocity(this.playerDirection);
            let xPosition = (this.snakeArray.at(-1).x + velocity[0]) % BOARD_SIZE_X;
            let yPosition = (this.snakeArray.at(-1).y + velocity[1]) % BOARD_SIZE_Y;

            if (yPosition < 0) {
                yPosition+=BOARD_SIZE_Y;
            }
            if (xPosition < 0) {
                xPosition+=BOARD_SIZE_X;
            }
            this.snakeArray.push({ y: yPosition, x: xPosition });
            
            // check if there is a collision
            const snakeHead = this.snakeArray.at(-1);
            if (this.snack.x === snakeHead.x && this.snack.y === snakeHead.y) {
                this.snack = { x: getRandomInt(BOARD_SIZE_X), y: getRandomInt(BOARD_SIZE_Y) };
            }
            else if (this.snakeArray.slice(0, this.snakeArray.length - 2).findIndex((val) => val.x === snakeHead.x && val.y === snakeHead.y) !== -1) {
                const maxSnakeLength = this.snakeArray.length;
                this.resetGame();
                alert(`Game over. Your snake was ${maxSnakeLength} segments long`);
            } else {
                this.snakeArray.splice(0, 1);
            }
            this.tick = this.tick + 1;
        }
        
        
        // draw!
        this.draw(0);
    }

    draw(delta) {
        // create the gameboard if it doesn't exist and then clear the screen
        if (document.getElementById(this.id) === null) {
            let gameBoard = document.createElement('div');
            gameBoard.className = "vine-box";
            gameBoard.id = this.id;
            gameBoard.style.position = 'absolute';
            gameBoard.style.height = `${BOARD_SIZE_Y * HEIGHT_OF_SEGMENT_Y}px`;
            gameBoard.style.width = `${BOARD_SIZE_X * HEIGHT_OF_SEGMENT_X}px`;
            document.body.append(gameBoard);
        }

        document.getElementById(this.id).innerText = "";

        // iterate over the snakeArray and draw these
        let segmentDirection = this.playerDirection;
        this.snakeArray.forEach((segment, idx) => {
            drawSegment(segment.x, segment.y, delta, segmentDirection, this.id);
        });

        // draw the snack
        drawSnack(this.snack.x, this.snack.y, this.id);
    }
}