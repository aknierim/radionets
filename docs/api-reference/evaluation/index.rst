.. _evaluation:

************************************
Evaluation (`~radionets.evaluation`)
************************************

.. currentmodule:: radionets.evaluation

Functions for the evaluation of the training sessions. The available
options reach from single, exemplary plots in :math:`(u, v)` space and image space
to methods computing characteristic values on large test datasets. In detail:

* Amplitude and phase for the prediction and the truth. Example image below includes
  the difference between prediction and truth.

 .. image:: ../../../resources/amp_phase.png
   :width: 800
   :alt: Amplitude and phase for the prediction and the truth.

* Reconstructed source images with additional features, such as MS-SSIM values or the
  viewing angle. Example image below.

 .. image:: ../../../resources/source_plot.png
   :width: 800
   :alt: Reconstructed source images.

* Histogram of differences between predicted and true viewing angles. The image includes a
  comparison to `wsclean <https://gitlab.com/aroffringa/wsclean>`_.

 .. image:: ../../../resources/hist_jet_offsets.png
   :width: 400
   :align: center
   :alt: Histogram of differences between predicted and true viewing angles.

* Histogram of the ratio between predicted and true source areas. The image includes a
  comparison to `wsclean <https://gitlab.com/aroffringa/wsclean>`_.

 .. image:: ../../../resources/hist_area_ratios.png
   :width: 400
   :align: center
   :alt: Histogram of the ratio between predicted and true source areas.

* Histogram of flux difference in the core component. The image includes a
  comparison to `wsclean <https://gitlab.com/aroffringa/wsclean>`_.

 .. image:: ../../../resources/hist_mean_diffs.png
   :width: 400
   :align: center
   :alt: Histogram of flux difference in the core component.

* Included, but not yet fully operational

  * Histogram of differences between predicted and true MS-SSIM values on a dedicated test dataset

  * Histogram of differences between predicted and true dynamic range values on a dedicated test dataset


All histograms are created on a dedicated test dataset.


Contents of the `~radionets.evaluation` Module
================================================

.. toctree::
  :maxdepth: 1
  :glob:

  */index
