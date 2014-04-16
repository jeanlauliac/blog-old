A Case for Makefiles in Node.js
###############################

:date: 2014-04-16 11:42
:slug: makefiles-in-node
:summary: Leveraging an “ancient” but well-tried technology for Web
          node.js projects

We see a lot of *build tools* -- or \`\`task runners'' -- being built in
the `node.js`_ world. `Grunt.js`_ seems to be the most popular one, along
with `gulp.js`_, brunch_, smoosh_, gear.js_... Those provide an all-in-one
solution, supported by a myriad of plugins. They are appealing for their
relative simplicity, and as such, provide a decent solution for most
projects.

There are alternatives, however, and they are not without strong arguments.
Let's not forget the `capability of simple npm scripts`__ for the simplest
projects. After all, `simplicity`_ is part of the node.js philosophy,
and it naturally makes projects uncomplicated.

For more complex situations like Web applications, you may also use a
:abbr:`UNIX`-ish, generic build system. The most well-known is probably `GNU
Make`_, but `Ninja`_ is another example. Instead of relying upon plugins,
they let the developer use any command-line statement. As such, they foster
*composability*, while plugins are more advocating configuration and
*extensibility*.

What does it mean? You can call a command-line tool without the need of any
build system. But you cannot use a grunt.js plugin outside of the tool
framework. Command-line tools can be written in any language: C++, Ruby, Python,
etc. A plugin can only be in JavaScript.

.. _node.js: http://nodejs.org/
.. _Grunt.js: http://gruntjs.com/
.. _gulp.js: http://gulpjs.com/
.. _brunch: http://brunch.io/
.. _smoosh: https://github.com/fat/smoosh
.. _gear.js: http://gearjs.org/
.. __: http://substack.net/task_automation_with_npm_run
.. _simplicity: http://blog.izs.me/post/
                48281998870/unix-philosophy-and-node-js
.. _GNU Make: https://www.gnu.org/software/make/
.. _Ninja: http://martine.github.io/ninja/

Going Incremental
=================

A build system like ``make`` tracks the state of each file involved, and calls
the underlying transformation tools only when necessary. In the following
example, the CoffeeScript_ transpiler_ is called only when ``foo.coffee``
has been modified since the last build:

.. code-block:: make

    BIN=node_modules/.bin/

    dest/foo.js: foo.coffee
        $(BIN)coffee -sc < $< > $@

Here ``$<`` and ``$@`` are `automatic variables`_ providing contextual
file paths. We also make sure to use the local CoffeeScript transpiler, because
we want to control the version. Calling ``make`` from the command line yields:

.. _automatic variables: https://www.gnu.org/software/make/manual/
                         html_node/Automatic-Variables.html

.. code-block:: bash

    make
    #=> node_modules/.bin/coffee -sc < foo.coffee > dest/foo.js
    make
    #=> make: Nothing to be done for `dest/foo.js'.

The behavior is called the *incremental build*, or sometimes \`\`minimal
rebuild''. This is especially useful on large projects, where it makes
development iterations faster.

.. _CoffeeScript: http://coffeescript.org/
.. _transpiler: http://en.wikipedia.org/wiki/Source-to-source_compiler

Where are my tasks?
===================

In addition to file targets, ``make`` can handle simple named tasks,
called *phony targets*. For example, a default task could be:

.. code-block:: make

    .PHONY: all
    all: jshint qunit concat uglify

This is the direct equivalent of registering a task as a list in ``grunt``:

.. code-block:: js

    grunt.registerTask('all', ['jshint', 'qunit', 'concat', 'uglify']);

Going Generic
=============

In a bunch of cases you will want to write general transformation rules. GNU
Make makes this pretty easy to do:

.. code-block:: make

    BIN=node_modules/.bin/

    .PHONY: all
    all: $(patsubst %.coffee,dest/%.js,$(wildcard *.coffee))

    dest/%.js: %.coffee
        $(BIN)coffee -sc < $< > $@

It is combined here with the `wildcard function`_ to avoid listing files
manually. For comparaison is the `globbing technique`_ in grunt.js:

.. code-block:: js

    // [...]
    coffee: {
        glob_to_multiple: {
            expand: true,
            flatten: true,
            cwd: '.',
            src: ['*.coffee'],
            dest: 'dest/',
            ext: '.js'
        }
    }

In a bunch of cases the grunt.js file will be simpler. This is partly because
plugins target specific use cases while the ``Makefile`` syntax is broader. The
benefit of ``make`` arise from its flexibility -- the ability to change
micro-behaviors. With plugins this is done by configuration, where you rely on
its implementor choices.

.. _wildcard function: http://www.gnu.org/software/make/manual/
                       make.html#Wildcard-Function
.. _globbing technique: https://www.npmjs.org/package/grunt-contrib-coffee

Let's Concat
============

Here is a more complete example: let's say we want to transpile all our
CoffeeScript sources to Javascript, then concatenate and minify them into a
``bundle.js``. Here's a possible solution:

.. code-block:: make

    BIN=node_modules/.bin/

    .PHONY: all
    all: bundle.js

    bundle.js: $(patsubst %.coffee,dest/%.js,$(wildcard *.coffee))
        cat $^ | uglifyjs -c - > $@

    dest/%.js: %.coffee
        $(BIN)coffee -sc < $< > $@

We just added an additional layer of processing to the ``Makefile``. Note how
similar it looks to the previous version. ``$^`` is another automatic variable
containing the name of all the prerequisites; here, the ``.js`` files.  With a
build tool, you may need a plugin for each step, with the proper
configuration and intermediate file.

This simple example lacks some features, notably the source
map generation. This could be done with a custom ``cat`` command and `specifying
an input source map to uglifyjs`__; but using a powerful module system like
`browserify`_ is probably better anyway.

.. __: https://github.com/mishoo/UglifyJS2#composed-source-map
.. _browserify: https://github.com/substack/node-browserify

Rebuild on Change
=================

A handy grunt.js plugins is grunt-contrib-watch_ that enables you to
execute tasks when some file changes; making development iterations faster.
How can we get this behavior with ``make``?

Apart from platform-specific APIs like inotify_, we can use node.js's own file
watching mechanism. The package supervisor_ exposes this feature as a
command-line tool. We can add a new phony target ``auto`` as such:

.. code-block:: make

    .PHONY: auto
    auto:
        $(BIN)supervisor -q -w . -e 'coffee' -n exit -x make all

``-n exit`` prevents ``supervisor`` from running ``make`` again and again.
``-x make`` replaces the default program (``node``) run by ``supervisor``.
``all`` will be passed as argument, the rule we defined before; so that
indeed the coffee files are retranspiled on change. Note that the
incremental build is still in action here: when a file change, only this one
is transpiled to JavaScript.

Let's imagine this is part of a static website build process: we may
want to serve the files in the ``dest`` directory over HTTP. The serve_
package and command-line tool can fulfill this goal:

.. code-block:: make

    .PHONY: auto
    auto:
        $(BIN)supervisor -q -w . -e 'coffee' -n exit -x make all &
        $(BIN)serve dest

Note how we use ``&`` at the end of the first line. This means the `commands
will be executed asynchonously`__ as interpreted by the shell; effectively
supervising and serving files at the same time. Interrupting the ``make``
process with ``Ctrl-C`` stops both.

We could add LiveReload_ as well using the tiny-lr_ package. Here again, it
exposes a command-line tool running a LiveReload server. You can then make
``POST`` requests with ``curl`` to signal changes as described in the
documentation.

.. _grunt-contrib-watch: https://www.npmjs.org/package/grunt-contrib-watch
.. _inotify: http://man7.org/linux/man-pages/man7/inotify.7.html
.. _supervisor: https://www.npmjs.org/package/supervisor
.. _LiveReload: http://livereload.com/
.. _tiny-lr: https://www.npmjs.org/package/tiny-lr
.. _serve: https://www.npmjs.org/package/serve
.. __: http://www.gnu.org/software/bash/manual/html_node/Lists.html#Lists

Conclusion
==========

Using a ``Makefile`` also enables you to use any version of the packages. They
don't necessarily have to be ``npm`` packages. For instance, you can use ruby
gems, like Sass_. With node.js build tools, some plugins use `broad specifiers`_
or `peerDependencies`_ to let you choose the version, but you're out of luck if
you want to use a newer, unsupported version. In this case, forking the plugin
may be necessary.

Using Makefiles is essentially bringing a bunch of small existing tools
and assembling them as building bricks. The tools themselves can be arbitrarily
complex and in any language, so you are not limited.

Now, for the ugly: yes, GNU Make on Windows can be a total pain. Similarly,
the shell that executes the command-lines -- ``cmd.exe`` -- lacks a lot of
``bash`` features. Some commands are not available or got different names,
like ``cat``. This may improve in the future, but Makefiles are clearly not
practical enough on Windows.

If however you are working on a :abbr:`UNIX`-only project -- including Linux and
OS X --, you may want to give it a try, and compare how well it performs
towards the now-usual node.js build tools: GNU Make is by no means obsolete.

.. _Sass: http://sass-lang.com/
.. _broad specifiers: https://www.npmjs.org/doc/json.html#dependencies
.. _peerDependencies: http://blog.nodejs.org/2013/02/07/peer-dependencies/

Further reading
---------------

* `Let's Make a Framework: JSLint, Makefiles <http://dailyjs.com/2011/08/11/
  framework-75/>`_;
* `Makefile recipes for node.js packages <http://andreypopp.com/posts/
  2013-05-16-makefile-recipes-for-node-js.html>`_;
* `Introducing Grunt <http://weblog.bocoup.com/introducing-grunt/>`_ talks about
  the initial idea behind making a replacement for ``make``;
* `Node.js, Ant, Grunt and other build tools <http://blog.millermedeiros.com/
  node-js-ant-grunt-and-other-build-tools/>`_ makes a point against plugins;
* `Why Grunt? Why not something else? <http://benalman.com/news/2012/08/
  why-grunt/>`_ is an answer to the above.
