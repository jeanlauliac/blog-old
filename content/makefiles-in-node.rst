Makefiles in Node.js
####################

:date: 2014-03-23 11:52
:slug: makefiles-in-node
:summary: Leveraging a well-tried technology for Web, node.js projects

We have seen a lot of \`\`build tools'' being built in the `node.js`_ world,
`grunt.js`_ and `gulp.js`_ seemingly being the most popular ones. Those provide
an all-in-one solution, supported by a myriad of plugins. They are appealing for
their relative simplicity. As such, they provide a quite decent solution for
most projects.

.. _node.js: http://nodejs.org/
.. _grunt.js: http://gruntjs.com/
.. _gulp.js: http://gulpjs.com/

There are alternatives, however, and they are not without strong arguments.
Let's not forget the `capability of simple npm scripts`__ for the simplest
projects. `Keeping things small`_ is part of the node.js philosophy: naturally
the technique is much useful for tiny libraries.

.. __: http://substack.net/task_automation_with_npm_run
.. _Keeping things small: http://blog.izs.me/post/
                          48281998870/unix-philosophy-and-node-js

For more complex situations like Web applications, you can use a
:abbr:`UNIX`-ish, generic build system. The most well-know is probably `GNU Make`_, but
`Ninja`_ is another example.

Instead of resting upon plugins, they let the developer use any command-line
statement. As such, they foster a greater reusability: command-line tools
express *composability*. Plugins express *extensibility*.

What does it mean? You can call a command-line tool without the need of any
build system. But you cannot use a grunt.js plugin outside from the tool
framework. Command-line tools can be written in any language: C++, Ruby, Python,
etc. A plugin can only be in JavaScript.

.. _GNU Make: https://www.gnu.org/software/make/
.. _Ninja: http://martine.github.io/ninja/

Why use a build system?
=======================

A build system like ``make`` tracks the state of each file involved, and call
the underlying transformation tools only when necessary. In the following
example, the CoffeeScript_ transpiler_ is called only when ``foo.coffee``
have been modified since the last build:

.. _CoffeeScript: http://coffeescript.org/
.. _transpiler: http://en.wikipedia.org/wiki/Source-to-source_compiler

.. code-block:: make

    foo.js: foo.coffee
        coffee < $< > $@

Here ``$<`` and ``$@`` are `automatic variables`_ providing contextual
file paths. Calling ``make`` from the command line yields:

.. _automatic variables: https://www.gnu.org/software/make/manual/
                         html_node/Automatic-Variables.html

.. code-block:: bash

    make
    #=> coffee < foo.coffee > foo.js
    make
    #=> make: Nothing to be done for `foo.js'.

This is an especially useful behavior on large projects with lots of files
to transpile. It makes development iterations faster.

In a bunch of cases you will want to write general transformation rules. GNU
Make makes this pretty easy to do:

.. code-block:: make

    %.js: %.coffee
        coffee < $< > $@


Where are my tasks?
===================

In addition to file dependencies, ``make`` can handle simple named tasks,
called *phony targets*. For example, a default task could be:

.. code-block:: make

    .PHONY: all
    all: jshint qunit concat uglify

This is the direct equivalent of registering a task as a list in ``grunt``:

.. code-block:: js

    grunt.registerTask('all', ['jshint', 'qunit', 'concat', 'uglify']);

Further reading
===============

* `Let's Make a Framework: JSLint, Makefiles <http://dailyjs.com/2011/08/11/framework-75/>`_
* `Makefile recipes for node.js packages <http://andreypopp.com/posts/2013-05-16-makefile-recipes-for-node-js.html>`_

