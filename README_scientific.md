# Upgrade your calculator to version 1.1

This update is based on the Python/Tkinter calculator from our conversation.
It upgrades the desktop app and adds scientific tests. It is source code, not
a Windows executable: your existing GitHub Actions workflow builds the new EXE.

## Files to copy into your existing project

| File | Action | Purpose |
| --- | --- | --- |
| app.py | Replace the existing file | Dark scientific interface, DEG/RAD switch, buttons and keyboard input |
| scientific.py | Add | Expression evaluation and calculator input behavior |
| test_scientific.py | Add | 15 automated test methods, including multiple example/error cases |
| README_scientific.md | Add | This guide |

Keep your existing calculator.py, test_calculator.py, requirements-dev.txt,
.gitignore, and .github/workflows/pipeline.yml. If you have made your own
changes to app.py, compare it with the supplied replacement before copying.
The update expects calculator.py to provide calculate(a, b, operation), as in
the original guide.

No additional runtime dependency is needed. The update uses Python's built-in
math, ast, and tkinter modules. Existing CI uses pytest; pytest also discovers
the unittest-style tests in test_scientific.py automatically.

## 1. Start a feature branch before copying the files

In PowerShell:

```powershell
cd C:\Users\Neeraj\cicd-calc
git status
```

Continue when your working tree is clean. If you have unsaved/uncommitted work,
save and commit the intended changes first. Do not discard them.

```powershell
git switch main
git pull --ff-only origin main
git switch -c feature/scientific-calculator
```

If any command fails, resolve that error before continuing. Now extract this
ZIP to a separate folder and copy its four files directly into cicd-calc,
beside your existing calculator.py. Do not place them in a nested subfolder.

## 2. Run locally

Activate your existing virtual environment if necessary:

```powershell
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements-dev.txt
python -m pytest -v
python app.py
```

If PowerShell activation is blocked, use the environment's interpreter directly:

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements-dev.txt
.\.venv\Scripts\python.exe -m pytest -v
.\.venv\Scripts\python.exe app.py
```

If the original nine tests are unchanged and there are no other tests in the
project, pytest should report 24 passing tests (9 original + 15 new).

## 3. Try the scientific calculator

The window starts at 440 x 660 pixels and can be resized. It starts in DEG mode.
Click DEG to switch to RAD, then press equals to recalculate the current formula.

| What to enter | Mode | Expected result |
| --- | --- | --- |
| sin(30) | DEG | 0.5 |
| cos(60) | DEG | 0.5 |
| tan(45) | DEG | approximately 1 |
| sin(pi/2) | RAD | 1 |
| sqrt(81) | Either | 9 |
| log(1000) | Either | 3 |
| ln(e) | Either | 1 |
| 2^3 | Either | 8 |
| fact(5) | Either | 120 |
| (2+3)*4 | Either | 20 |
| sqrt(-1) | Either | Error with an explanatory message |
| 1/0 | Either | Error with an explanatory message |

Button examples:

- sin, 3, 0, ), = calculates sin(30).
- The square-root button inserts sqrt(; the n! button inserts fact(. Enter the
  argument and close the parenthesis before pressing equals.
- x-y power (xʸ) inserts ^. For 2 cubed, press 2, xʸ, 3, =.
- x², 1/x, and +/- wrap the current expression, or use the result after equals.
- Ans inserts the previous successful result. For its square root, press sqrt,
  Ans, ), =.
- After a result, a number starts a new formula; an arithmetic operator continues
  from the full-precision result. Pressing equals repeatedly leaves the result
  unchanged (it does not repeat the last operation).
- AC clears the formula, result, and Ans. The selected angle mode is retained.
- Input appends at the end. Backspace deletes the last character. The expression
  display scrolls horizontally for long input; cursor-based editing is not added.
- Type function names in lowercase. Enter calculates, Escape clears.

Use explicit multiplication: 2*pi and 2*sin(30), not 2pi or 2sin(30).
log means base 10; ln means natural logarithm. ^ and ** both mean exponentiation.
The calculator supports real numbers; square roots of negative numbers are errors.
Factorials accept whole numbers from 0 through 170. This calculator uses standard
floating-point arithmetic, so results are approximate and the display rounds to
12 significant digits. Large factorials are approximate, not exact big integers.
Ans retains the underlying float precision. Expressions are limited to 300
characters and a bounded number of syntax nodes to keep input manageable.

## 4. Commit and push the upgrade

```powershell
git add app.py scientific.py test_scientific.py README_scientific.md
git commit -m "Add scientific calculator and regression tests"
git push -u origin feature/scientific-calculator
```

On GitHub open a pull request with base main and compare
feature/scientific-calculator. Your original workflow does not run for a feature
branch push alone; the pull request triggers the tests.

Wait for Test calculator to pass and check the app manually before merging.
Build and publish application is expected to be skipped on the pull request.

## 5. Merge and publish the new version

After merging the pull request on GitHub:

```powershell
git switch main
git pull --ff-only origin main
git tag v1.1.0
git push origin v1.1.0
```

Use a new, unused version tag. If v1.1.0 already exists, choose another unused
version such as v1.1.1; do not move an existing release tag.

Your existing workflow's tag trigger runs the tests, builds app.py into
Calculator.exe with PyInstaller, and publishes a GitHub Release. No YAML change
is needed for the workflow previously supplied: python -m pytest -v discovers
the new tests, and PyInstaller follows the new scientific.py import.

## 6. Download the new application

Open https://github.com/neerajkotla2003-commits/Calculator/releases and select the
new version. Under Assets, download Calculator.exe. The name remains the same,
so use the release tag to identify the correct download.

Close the old application before replacing your old downloaded copy. Run the new
one: its title should read Scientific Calculator | 1.1. Repeat the examples above.
Your existing installed/downloaded EXE does not update itself automatically.

## What changed, and how it was checked

scientific.py reads an expression into an AST and evaluates only allowed numeric
operations, constants, and named functions. It does not execute arbitrary Python
with eval(). Basic operations still call your existing calculate function.
The GUI is separated from the evaluator and input state so CI can test behavior
without opening a desktop window.

During preparation, all 15 new unittest methods passed using the original
calculator.py from this conversation, and the app module imported successfully.
The tests cover precedence, real scientific functions, angle modes, invalid input,
size limits, previous-answer behavior, and editing after a result/error. The
Windows GUI and Windows EXE were not run in this environment; test them on your
machine and let your Windows GitHub Actions runner build the release.

Python references:
- https://docs.python.org/3/library/math.html
- https://docs.python.org/3/library/ast.html

If GitHub test collection unexpectedly names a different test file explicitly
instead of running pytest across the project, update it to python -m pytest -v.
The workflow originally provided already uses that command.
