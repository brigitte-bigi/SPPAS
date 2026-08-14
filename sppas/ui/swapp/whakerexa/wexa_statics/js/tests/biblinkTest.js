/**
:filename: tests.js.biblinkTest.js
:author: Brigitte Bigi
:contact: contact@sppas.org
:summary: Test file of the Link class.

.. _This file is part of Whakerexa: https://github.com/brigitte-bigi/Whakerexa ,
.. on 2026-07-28.
    -------------------------------------------------------------------------

    Copyright (C) 2026 Brigitte Bigi
    Laboratoire Parole et Langage, Aix-en-Provence, France

    Use of this software is governed by the GNU Public License, version 3.

    Whakerexa is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    Whakerexa is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with Whakerexa. If not, see <https://www.gnu.org/licenses/>.

    This banner notice must not be removed.

    -------------------------------------------------------------------------

*/

// instantiate unit tests class
let link_tests = new UnitTest();


// -----------------------------------------------------------------------
// The address is kept as written, so that it can be printed in full.
// Requirement B21.
// -----------------------------------------------------------------------

link_tests.add_test(() => {
    const address = 'https://hal.science/hal-03794830';
    const link = new Link(address);

    UnitTest.assert_values_equals(address, link.address, "link_address_test");
});

// -----------------------------------------------------------------------
// What an address leads to is read in the address, never in the name of
// the BibTeX field it came from. Requirement B12.
// -----------------------------------------------------------------------

link_tests.add_test(() => {
    const pdf = new Link('http://www.lrec-conf.org/proceedings/lrec2022/pdf/2022.lrec-1.104.pdf');

    UnitTest.assert_values_equals(LinkKind.PDF, pdf.kind(), "link_kind_pdf_test");
});

link_tests.add_test(() => {
    const hal = new Link('https://hal.science/hal-05474165');
    const old_hal = new Link('https://hal.archives-ouvertes.fr/hal-03794830');
    const arxiv = new Link('https://arxiv.org/abs/2402.01234');

    UnitTest.assert_values_equals(LinkKind.REPOSITORY, hal.kind(), "link_kind_hal_test");
    UnitTest.assert_values_equals(LinkKind.REPOSITORY, old_hal.kind(), "link_kind_old_hal_test");
    UnitTest.assert_values_equals(LinkKind.REPOSITORY, arxiv.kind(), "link_kind_arxiv_test");
});

link_tests.add_test(() => {
    const doi = new Link('https://doi.org/10.4000/tipa.5424');
    const publisher = new Link('https://www.tandfonline.com/doi/full/10.1080/24751839.2025.2611605');

    UnitTest.assert_values_equals(LinkKind.PUBLISHER, doi.kind(), "link_kind_doi_test");
    UnitTest.assert_values_equals(LinkKind.PUBLISHER, publisher.kind(), "link_kind_publisher_test");
});

// -----------------------------------------------------------------------
// An address that nothing recognizes is still a link, and is shown as
// such rather than dropped.
// -----------------------------------------------------------------------

link_tests.add_test(() => {
    const other = new Link('https://www.sppas.org/');

    UnitTest.assert_values_equals(LinkKind.OTHER, other.kind(), "link_kind_other_test");
});

// -----------------------------------------------------------------------
// The kind is read again from the address every time, and never stored.
// -----------------------------------------------------------------------

link_tests.add_test(() => {
    const link = new Link('https://hal.science/hal-05474165');

    UnitTest.assert_values_equals(link.kind(), link.kind(), "link_kind_stable_test");
});


// -----------------------------------------------------------------------
// Every field has its own archives: a document adds the ones it cites.
// -----------------------------------------------------------------------

link_tests.add_test(() => {
    const link = new Link('https://openaccess.example.org/record/12345');

    UnitTest.assert_values_equals(LinkKind.OTHER, link.kind(), "link_unknown_archive_test");

    Link.addRepositoryHosts('openaccess.example.org');
    UnitTest.assert_values_equals(LinkKind.REPOSITORY, link.kind(), "link_added_archive_test");

    Link.resetRepositoryHosts();
    UnitTest.assert_values_equals(LinkKind.OTHER, link.kind(), "link_reset_archive_test");
});

// -----------------------------------------------------------------------
// Adding a host twice leaves the list as it was.
// -----------------------------------------------------------------------

link_tests.add_test(() => {
    const before = Link.repositoryHosts.length;

    Link.addRepositoryHosts('hal.science');
    UnitTest.assert_values_equals(before, Link.repositoryHosts.length, "link_add_known_host_test");

    Link.resetRepositoryHosts();
});

// -----------------------------------------------------------------------
// A host can be removed, and a reference stops being seen as an archive.
// -----------------------------------------------------------------------

link_tests.add_test(() => {
    const link = new Link('https://arxiv.org/abs/2402.01234');

    Link.deleteRepositoryHosts('arxiv.org');
    UnitTest.assert_values_equals(LinkKind.OTHER, link.kind(), "link_deleted_archive_test");

    Link.resetRepositoryHosts();
    UnitTest.assert_values_equals(LinkKind.REPOSITORY, link.kind(), "link_reset_deleted_archive_test");
});

// -----------------------------------------------------------------------
// The list is only changed through the methods made for it.
// -----------------------------------------------------------------------

link_tests.add_test(() => {
    const hosts = Link.repositoryHosts;
    hosts.push('nowhere.example.org');

    UnitTest.assert_array_not_contains('nowhere.example.org', Link.repositoryHosts,
        "link_hosts_copy_test");
});


// launch all unit tests added
link_tests.launch_unit_test();
