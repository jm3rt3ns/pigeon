function assertEqual(x, y) {
    if (x !== y) {
        throw new Error(`${x} does not equal ${y}`);
    }
}

function assertNotEqual(x, y) {
    if (x === y) {
        throw new Error(`${x} equals ${y}`);
    }
}

function testCode() {
    // ensure createLink(x,y) returns a div element at the specified location
    const result = drawSegment(1,1,0,Directions.North); // each div is 50,50, so at the position (1,1), the div starts at (50, 50)
    assertEqual(result.offsetLeft, 25);
    assertEqual(result.offsetTop, 25);
    result.remove();

    // // test 2
    const result2 = drawSnack(0, 0);
    assertEqual(result2.style.backgroundColor, 'rgb(245, 72, 66)');
    result2.remove();

    // call the game cycle function and ensure the snake moves
    g = new Game();
    g.cycle(0);
    const segment = document.querySelector('.snake-segment');
    const snack = document.getElementById('snack');
    assertNotEqual(segment, null);
    assertNotEqual(snack, null);

    assertEqual(g.playerDirection, Directions.North);
    
    document.dispatchEvent(new KeyboardEvent('keyup',{'code':'ArrowLeft'}));
    assertEqual(g.playerDirection, Directions.West);
    
    document.dispatchEvent(new KeyboardEvent('keyup',{'code':'ArrowRight'}));
    assertEqual(g.playerDirection, Directions.East);
    
    document.dispatchEvent(new KeyboardEvent('keyup',{'code':'ArrowDown'}));
    assertEqual(g.playerDirection, Directions.South);

    // // wait 1 second and check if the tick is at 1
    const initialTick = g.tick;
    setTimeout(() => {
        assertEqual(initialTick + 15, g.tick);
    }, 1500);
}

testCode();