A Case for Makefiles in Node.js
###############################

:date: 2014-03-23 11:52
:slug: makefiles-in-node
:summary: Leveraging an “ancient” but well-tried technology for Web,
          node.js projects
:status: draft

We have seen a lot of *build tools* -- or \`\`task runners'' -- being built in
the `node.js`_ world, `grunt.js`_ seemingly being the most popular one, along
with `gulp.js`_, brunch_, smoosh_, gear.js_... Those provide an all-in-one
solution, supported by a myriad of plugins. They are appealing for their
relative simplicity, and as such, provide a quite decent solution for most
projects.

.. _node.js: http://nodejs.org/
.. _grunt.js: http://gruntjs.com/
.. _gulp.js: http://gulpjs.com/
.. _brunch: http://brunch.io/
.. _smoosh: https://github.com/fat/smoosh
.. _gear.js: http://gearjs.org/

There are alternatives, however, and they are not without strong arguments.
Let's not forget the `capability of simple npm scripts`__ for the simplest
projects. After all, `keeping things small`_ is part of the node.js philosophy,
and it naturally makes projects uncomplicated.

.. __: http://substack.net/task_automation_with_npm_run
.. _keeping things small: http://blog.izs.me/post/
                          48281998870/unix-philosophy-and-node-js

For more complex situations like Web applications, you may also use a
:abbr:`UNIX`-ish, generic build system. The most well-known is probably `GNU
Make`_, but `Ninja`_ is another example. Instead of resting upon plugins,
they let the developer use any command-line statement. As such, they foster
*composability*, while plugins express *extensibility*.

.. _GNU Make: https://www.gnu.org/software/make/
.. _Ninja: http://martine.github.io/ninja/

What does it mean? You can call a command-line tool without the need of any
build system. But you cannot use a grunt.js plugin outside from the tool
framework. Command-line tools can be written in any language: C++, Ruby, Python,
etc. A plugin can only be in JavaScript.

Going Incremental
=================

A build system like ``make`` tracks the state of each file involved, and call
the underlying transformation tools only when necessary. In the following
example, the CoffeeScript_ transpiler_ is called only when ``foo.coffee``
have been modified since the last build:

.. _CoffeeScript: http://coffeescript.org/
.. _transpiler: http://en.wikipedia.org/wiki/Source-to-source_compiler

.. code-block:: make

    dest/foo.js: foo.coffee
        coffee -sc < $< > $@

Here ``$<`` and ``$@`` are `automatic variables`_ providing contextual
file paths. Calling ``make`` from the command line yields:

.. _automatic variables: https://www.gnu.org/software/make/manual/
                         html_node/Automatic-Variables.html

.. code-block:: bash

    make
    #=> coffee -sc < foo.coffee > dest/foo.js
    make
    #=> make: Nothing to be done for `dest/foo.js'.

The behavior is called the *incremental build*, or sometimes \`\`minimal
rebuild''. This is especially useful on large projects, where it makes
development iterations faster.

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

    .PHONY: all
    all: $(patsubst %.coffee,dest/%.js,$(wildcard *.coffee))

    dest/%.js: %.coffee
        coffee -sc < $< > $@

It is combined with the `wildcard function`_ to avoid listing files manually.
Arguably, it is easier or not to read than -- for example -- the `globbing
technique`_ in grunt.js:

.. _wildcard function: http://www.gnu.org/software/make/manual/
                       make.html#Wildcard-Function
.. _globbing technique: https://www.npmjs.org/package/grunt-contrib-coffee

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

In a lot of cases the grunt.js file will be simpler. This is partly because
plugins target specific use cases while the ``Makefile`` syntax is broad. The
benefit of ``make``, then, will come from its flexibility -- the ability to
change micro-behaviors. With plugins this is done by configuration. With
``make`` this is done by changing the composition of the ``Makefile`` or the
command-lines.

Let's Concat
============

Here is a last example: let's say we want to compile all our coffee scripts to
Javascript, then concatenate and minify them into a `bundle.js`. Here's what we
get:

.. code-block:: make

    .PHONY: all
    all: bundle.js

    bundle.js: $(patsubst %.coffee,dest/%.js,$(wildcard *.coffee))
        cat $^ | uglifyjs -c - > $@

    dest/%.js: %.coffee
        coffee -sc < $< > $@

``$^`` is another automatic variable containing the name of all the
prerequisites; here, the ``.js`` files. We just added an additional layer of
processing to the ``Makefile``. With a build tool, you would need a plugin for
each step, with the proper configuration; this can be easier or harder depending
on the plugin author goals.

This simple example lacks some features, notably the source
map generation. This could be done with a custom ``cat`` command and `specifying
an input source map to uglifyjs`__.

.. __: https://github.com/mishoo/UglifyJS2#composed-source-map

Final Words
===========

Using a ``Makefile`` also let you use whatever version of the packages
containing command-line tools. They don't even have to be ``npm`` packages:
you may use ruby gems, etc. -- Sass_ comes to mind. With node.js build tools,
some plugins use the `peerDependencies field`_ to let you choose the version,
but it is not always implemented. In this case, you may have to fork the plugin
to be able to use a specific version.

Now, for the ugly: yes, GNU Make on Windows can be a total pain. Similarly,
the shell that execute the command-lines -- ``cmd.exe`` -- lacks a lot of
``bash`` features. Some commands are not available or got different names,
like ``cat``. This may improve in the future, but Makefiles are clearly not
practical enough on Windows.

If however you are working on a :abbr:`UNIX`-only project -- including Linux and
OS X --, you may want to give it a try, and compare how well it performs
towards the now-usual node.js build tools.

.. _Sass: http://sass-lang.com/
.. _peerDependencies field: http://blog.nodejs.org/2013/02/07/peer-dependencies/

Further reading
---------------

* `Let's Make a Framework: JSLint, Makefiles <http://dailyjs.com/2011/08/11/framework-75/>`_;
* `Makefile recipes for node.js packages <http://andreypopp.com/posts/2013-05-16-makefile-recipes-for-node-js.html>`_;
* `Introducing Grunt <http://weblog.bocoup.com/introducing-grunt/>`_ talks about
  the initial idea behind making a replacement for ``make``;
* `Node.js, Ant, Grunt and other build tools <http://blog.millermedeiros.com/node-js-ant-grunt-and-other-build-tools/>`_ makes a point against plugins;
* `Why Grunt? Why not something else? <http://benalman.com/news/2012/08/why-grunt/>`_ is an
  answer to the above.
